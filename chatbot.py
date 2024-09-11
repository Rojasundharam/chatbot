import os
import pickle
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
from anthropic import Anthropic
import docx
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google_drive_utils import get_drive_service, get_documents, get_document_content
from embedding_utils import EmbeddingUtil

# Load environment variables
load_dotenv()

# Check if environment variables are loaded
print("GOOGLE_DRIVE_FOLDER_ID:", os.getenv("GOOGLE_DRIVE_FOLDER_ID"))
print("ANTHROPIC_API_KEY:", os.getenv("ANTHROPIC_API_KEY"))
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDocument:
    def __init__(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata
        self.chunks: List[str] = []
        self.embeddings: List[List[float]] = []
        self.last_updated: datetime = datetime.now()

    def chunk_content(self, chunk_size: int = 1000):
        self.chunks = [self.content[i:i+chunk_size] for i in range(0, len(self.content), chunk_size)]

    def create_embeddings(self, embedding_util: EmbeddingUtil):
        self.embeddings = embedding_util.create_embeddings(self.chunks)

class ChatBot:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.drive_service = get_drive_service()
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        if not self.folder_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable is not set")
        self.documents: Dict[str, EnhancedDocument] = {}
        self.embedding_util = EmbeddingUtil()
        self.cache_file = 'chatbot_cache.pkl'
        self.cache_refresh_interval = timedelta(hours=24)
        
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        
        self.load_or_update_documents()

    def load_or_update_documents(self):
        if self.should_refresh_cache():
            logger.info("Cache is outdated or doesn't exist. Refreshing documents from Google Drive.")
            self.fetch_and_process_documents()
            self.save_cache()
        else:
            self.load_cache()

    def should_refresh_cache(self) -> bool:
        if not os.path.exists(self.cache_file):
            return True
        last_modified = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
        return datetime.now() - last_modified > self.cache_refresh_interval

    def load_cache(self):
        try:
            with open(self.cache_file, 'rb') as f:
                self.documents = pickle.load(f)
            logger.info(f"Loaded {len(self.documents)} documents from cache.")
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            self.documents = {}

    def save_cache(self):
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.documents, f)
            logger.info(f"Saved {len(self.documents)} documents to cache.")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    def fetch_and_process_documents(self):
        self.documents.clear()  # Clear existing documents before fetching new ones
        files = get_documents(self.drive_service, self.folder_id)
        for file in files:
            try:
                content = self._get_file_content(file['id'], file['name'])
                doc = EnhancedDocument(file['id'], content, file)
                doc.chunk_content()
                doc.create_embeddings(self.embedding_util)
                self.documents[file['id']] = doc
                self._update_db_document(doc)
                logger.info(f"Successfully processed file: {file['name']}")
            except Exception as e:
                logger.error(f"Error processing file {file['name']}: {str(e)}")

    def _get_file_content(self, file_id: str, file_name: str) -> str:
        content = get_document_content(self.drive_service, file_id)
        if file_name.lower().endswith('.docx'):
            doc = docx.Document(io.BytesIO(content))
            return '\n'.join([para.text for para in doc.paragraphs])
        else:
            return content.decode('utf-8', errors='ignore')

    def _update_db_document(self, doc: EnhancedDocument):
        # Implement this method to update or insert the document in your database
        pass

    def get_relevant_context(self, query: str, max_chunks: int = 5) -> str:
        query_embedding = self.embedding_util.create_embeddings([query])[0]
        relevant_chunks = []
        for doc in self.documents.values():
            similarities = [self.embedding_util.compute_similarity(query_embedding, chunk_embedding) 
                            for chunk_embedding in doc.embeddings]
            top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:max_chunks]
            relevant_chunks.extend([doc.chunks[i] for i in top_indices])
        
        return "\n\n".join(relevant_chunks[:max_chunks])

    def process_user_input(self, user_input: str) -> str:
        try:
            logger.info(f"Processing user input: {user_input}")
            context = self.get_relevant_context(user_input)
            
            if not context.strip():
                return "I'm sorry, but I couldn't find any specific information related to your query in the documents."

            prompt = f"""Based on the following information from the documents, answer the user's question:

Context:
{context}

User Question: {user_input}

Instructions:
1. Use ONLY the information provided in the context above to answer the question.
2. If the context doesn't contain specific information that answers the user's question, say so.
3. Do not include any information or assumptions that are not explicitly stated in the provided context.
4. Begin your response with "Based on the available information:" to emphasize that the answer comes from the documents.

Answer:
"""

            response = self.anthropic.completions.create(
                model="claude-2.1",
                prompt=prompt,
                max_tokens_to_sample=300,
            )
            
            assistant_response = response.completion
            logger.info(f"Generated response: {assistant_response[:100]}...")
            return assistant_response
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question?"

def initialize_chatbot():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db_session = SessionLocal()
        
        return ChatBot(db_session)
    except Exception as e:
        logger.error(f"Error initializing ChatBot: {str(e)}")
        raise

if __name__ == "__main__":
    chatbot = initialize_chatbot()
    chatbot.chat()