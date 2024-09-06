import os
import pickle
import re
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
from anthropic import Anthropic
from config import IDENTITY, TOOLS, MODEL, RAG_PROMPT
from google_drive_utils import get_drive_service, get_documents, get_document_content
from embedding_utils import EmbeddingUtil
from file_processor import extract_file_text, get_file_ext
import logging
import numpy as np

load_dotenv()

CACHE_FILE = 'chatbot_cache.pkl'
CACHE_EXPIRY_HOURS = 24

class ChatBot:
    def __init__(self, session_state):
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
            self.anthropic = Anthropic(api_key=api_key)
            self.session_state = session_state
            self.drive_service = get_drive_service()
            self.folder_id = "1EyR0sfFEBUDGbPn3lBDIP5qcFumItrvQ"
            
            self.embedding_util = EmbeddingUtil()
            self.load_or_update_cache()
            
            logging.info("ChatBot initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ChatBot: {str(e)}")
            raise

    def load_or_update_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                cache_data = pickle.load(f)
            
            if datetime.now() - cache_data['timestamp'] < timedelta(hours=CACHE_EXPIRY_HOURS):
                self.documents = cache_data['documents']
                self.embeddings = cache_data['embeddings']
                self.index = cache_data['index']
                self.tfidf_matrix = cache_data['tfidf_matrix']
                self.embedding_util.tfidf_vectorizer = cache_data['tfidf_vectorizer']
                logging.info("Loaded data from cache")
                return

        self.update_cache()

    def update_cache(self):
        self.documents = self.load_documents()
        if not self.documents:
            logging.error("No documents were loaded. Cannot update cache.")
            return

        self.embeddings = self.embedding_util.create_embeddings(self.documents)
        self.index = self.embedding_util.create_faiss_index(self.embeddings)
        self.tfidf_matrix = self.embedding_util.create_tfidf_matrix(self.documents)

        cache_data = {
            'timestamp': datetime.now(),
            'documents': self.documents,
            'embeddings': self.embeddings,
            'index': self.index,
            'tfidf_matrix': self.tfidf_matrix,
            'tfidf_vectorizer': self.embedding_util.tfidf_vectorizer
        }

        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache_data, f)
        
        logging.info("Updated and saved cache")

    def load_documents(self):
        files = get_documents(self.drive_service, self.folder_id)
        documents = []
        for file in files:
            content = get_document_content(self.drive_service, file['id'])
            file_extension = get_file_ext(file['name'])
            
            try:
                # Create a BytesIO object from the content
                file_like_object = io.BytesIO(content)
                
                # Pass the file name and the file-like object to extract_file_text
                extracted_text = extract_file_text(file['name'], file_like_object)
                
                processed_content = self.preprocess_text(extracted_text)
                documents.append(processed_content)
                logging.info(f"Loaded and preprocessed document: {file['name']}")
            except Exception as e:
                logging.error(f"Failed to process file {file['name']}: {str(e)}")
        
        return documents

    def preprocess_text(self, text):
        # Remove special characters but keep spaces between words
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        # Convert to lowercase and remove extra spaces
        return ' '.join(text.lower().split())

    def expand_query(self, query):
        expanded_terms = {
            "jkkn": ["j.k.k. nattraja", "educational institutions", "college", "university", "school", "academy"],
            "course": ["program", "curriculum", "study", "degree", "major", "subject", "class"],
            "admission": ["enrollment", "registration", "apply", "join", "entrance", "application"],
            "facility": ["infrastructure", "amenity", "resource", "campus", "building", "laboratory", "library"],
            "faculty": ["staff", "teacher", "professor", "lecturer", "instructor"],
            "student": ["learner", "pupil", "scholar", "undergraduate", "postgraduate"],
            "research": ["study", "investigation", "project", "thesis", "dissertation"],
        }
        expanded_query = query.lower()
        for term, expansions in expanded_terms.items():
            if term in expanded_query:
                expanded_query += " " + " ".join(expansions)
        return expanded_query

    def get_relevant_context(self, query, max_tokens=50000, top_k=20):
        similar_indices = self.embedding_util.hybrid_search(query, self.index, self.embeddings, self.tfidf_matrix, k=top_k)
        
        context = ""
        total_tokens = 0
        for i in similar_indices:
            document = self.documents[i]
            document_tokens = self.anthropic.count_tokens(document)
            if total_tokens + document_tokens > max_tokens:
                break
            context += document + "\n\n"
            total_tokens += document_tokens
        
        logging.info(f"Retrieved context (first 500 chars): {context[:500]}")
        return context

    def process_user_input(self, user_input):
        try:
            logging.info(f"Processing user input: {user_input}")
            
            # Check for greetings or general queries
            greetings = ["hi", "hello", "hey", "greetings"]
            general_queries = ["how are you", "what can you do"]
            
            if user_input.lower() in greetings:
                return "Hello! Welcome to JKKN Assist. How can I help you with information about JKKN Educational Institutions today?"
            
            if any(query in user_input.lower() for query in general_queries):
                return "I'm an AI assistant designed to provide information about JKKN Educational Institutions. I can help you with details about courses, admissions, facilities, and more. What would you like to know?"
            
            expanded_query = self.expand_query(user_input)
            logging.info(f"Expanded query: {expanded_query}")
            context = self.get_relevant_context(expanded_query)
            
            if not context.strip():
                logging.warning("No relevant context found")
                return "I'm sorry, but I couldn't find any specific information related to your query. Could you please ask a more detailed question about JKKN institutions, such as about specific courses, admissions processes, or facilities?"

            rag_message = f"""Based on the following information from JKKN institutional documents, please answer the user's question:

Context:
{context}

User Question: {user_input}

Instructions:
1. Use ONLY the information provided in the context above to answer the question.
2. If the context doesn't contain relevant information, say so and offer to help with related topics about JKKN institutions.
3. Provide a concise but informative answer, citing specific details from the context when possible.
4. If you're unsure about any information, state that clearly rather than making assumptions.

Answer:
"""

            response_message = self.generate_message([{"role": "user", "content": rag_message}])
            assistant_response = response_message.content[0].text
            logging.info(f"Generated response: {assistant_response[:100]}...")  # Log first 100 chars of response
            return assistant_response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}. Could you please try asking your question about JKKN institutions in a different way?"

    def generate_message(self, messages, max_tokens=2048):
        try:
            response = self.anthropic.messages.create(
                model=MODEL,
                system=IDENTITY,
                max_tokens=max_tokens,
                messages=messages,
                tools=TOOLS,
            )
            return response
        except Exception as e:
            logging.error(f"Error generating message: {str(e)}")
            raise

    def get_conversation_history(self):
        return self.session_state.messages