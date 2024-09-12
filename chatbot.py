import os
from dotenv import load_dotenv
import logging
from google_drive_utils import get_drive_service, index_documents
from embedding_utils import EmbeddingUtil
from anthropic import Anthropic
from transformers import pipeline

# Load environment variables
load_dotenv()

class ChatBot:
    def __init__(self, session_state):
        self.session_state = session_state
        
        # Check for Google credentials
        google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not google_creds_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. Please set it to the path of your Google Cloud service account key file.")
        
        self.drive_service = get_drive_service()
        self.folder_id = "1EyR0sfFEBUDGbPn3lBDIP5qcFumItrvQ"  # Your Google Drive folder ID
        
        self.embedding_util = EmbeddingUtil()
        
        # Check for Anthropic API key
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please set it to your Anthropic API key.")
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        
        self.qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        
        self.documents = self.index_documents()
        self.index_and_vectorize_documents()

    def index_documents(self):
        try:
            documents = index_documents(self.drive_service, self.folder_id)
            if not documents:
                print("No documents were successfully indexed. The chatbot may not have any information to work with.")
            return documents
        except Exception as e:
            print(f"Error during document indexing: {str(e)}")
            return []

    def index_and_vectorize_documents(self):
        if not self.documents:
            print("No documents to vectorize. The chatbot may not be able to provide accurate responses.")
            return
        
        texts = [doc['content'] for doc in self.documents]
        doc_ids = [doc['id'] for doc in self.documents]
        embeddings = self.embedding_util.create_embeddings(texts)
        self.embedding_util.create_faiss_index(embeddings, doc_ids)

    def process_user_input(self, user_input: str) -> str:
        try:
            similar_doc_ids = self.embedding_util.search_similar(user_input, k=3)
            context = self.get_context_from_ids(similar_doc_ids)
            
            extracted_answer = self.extract_answer(user_input, context)
            
            rag_message = f"""Based on the following extracted answer and context from JKKN institutional documents, provide a comprehensive response to the user's question:

            Extracted Answer: {extracted_answer}

            Context:
            {context}

            User Question: {user_input}

            Instructions:
            1. Use the extracted answer and context to formulate a detailed response.
            2. If the extracted answer doesn't seem relevant, rely more on the context.
            3. Begin your response with "According to the JKKN documents:" to emphasize that the information comes directly from the institution's materials.
            4. Provide ALL relevant information, even if it seems repetitive or extensive.

            Answer:
            """

            response_message = self.generate_message([{"role": "user", "content": rag_message}])
            assistant_response = response_message.content[0].text
            return assistant_response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question about JKKN institutions?"

    def get_context_from_ids(self, doc_ids):
        relevant_docs = [doc['content'] for doc in self.documents if doc['id'] in doc_ids]
        return "\n\n".join(relevant_docs)

    def extract_answer(self, question, context):
        if not context:
            return "I'm sorry, but I don't have enough information to answer that question accurately."
        result = self.qa_model(question=question, context=context)
        return result['answer']

    def generate_message(self, messages, max_tokens=2048):
        try:
            response = self.anthropic.messages.create(
                model="claude-2.1",
                max_tokens=max_tokens,
                messages=messages
            )
            return response
        except Exception as e:
            logging.error(f"Error generating message: {str(e)}")
            raise

    def get_top_documents(self, user_input: str, k: int = 3) -> list:
        similar_doc_ids = self.embedding_util.search_similar(user_input, k=k)
        top_docs = []
        for doc_id in similar_doc_ids:
            doc = next((doc for doc in self.documents if doc['id'] == doc_id), None)
            if doc:
                top_docs.append({
                    'name': doc['name'],
                    'id': doc['id']
                })
        return top_docs