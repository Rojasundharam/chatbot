import os
from dotenv import load_dotenv
from anthropic import Anthropic
from config import IDENTITY, TOOLS, MODEL, RAG_PROMPT
from google_drive_utils import get_drive_service, get_documents, get_document_content
from embedding_utils import EmbeddingUtil
import logging
import numpy as np

load_dotenv()

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
            self.documents = self.load_documents()
            self.embedding_util = EmbeddingUtil()
            self.embeddings = self.embedding_util.create_embeddings(self.documents)
            self.index = self.embedding_util.create_faiss_index(self.embeddings)
            self.tfidf_matrix = self.embedding_util.create_tfidf_matrix(self.documents)
            logging.info("ChatBot initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ChatBot: {str(e)}")
            raise

    def load_documents(self):
        files = get_documents(self.drive_service, self.folder_id)
        documents = []
        for file in files:
            content = get_document_content(self.drive_service, file['id'])
            content = self.preprocess_text(content)
            documents.append(content)
            logging.info(f"Loaded and preprocessed document: {file['name']}")
        return documents

    def preprocess_text(self, text):
        return text.lower().replace('\n', ' ')

    def get_relevant_context(self, query, max_tokens=50000):
        similar_indices = self.embedding_util.hybrid_search(query, self.index, self.embeddings, self.tfidf_matrix)
        
        context = ""
        total_tokens = 0
        for i in similar_indices:
            document = self.documents[i]
            document_tokens = self.anthropic.count_tokens(document)
            if total_tokens + document_tokens > max_tokens:
                break
            context += document + "\n\n"
            total_tokens += document_tokens
        return context

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

    def expand_query(self, query):
        expanded_terms = {
            "course": ["program", "curriculum", "study"],
            "admission": ["enrollment", "registration", "apply"],
            "facility": ["infrastructure", "amenity", "resource"],
        }
        expanded_query = query
        for term, expansions in expanded_terms.items():
            if term in query.lower():
                expanded_query += " " + " ".join(expansions)
        return expanded_query

    def process_user_input(self, user_input):
        try:
            logging.info(f"Processing user input: {user_input}")
            expanded_query = self.expand_query(user_input)
            logging.info(f"Expanded query: {expanded_query}")
            context = self.get_relevant_context(expanded_query)
            
            if not context:
                logging.warning("No relevant context found")
                return "I'm sorry, but I couldn't find any relevant information in my knowledge base to answer your question. Could you please rephrase or ask about a different topic related to JKKN institutions?"

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
            return "I apologize, but I encountered an error while processing your request. Could you please try asking your question about JKKN institutions in a different way?"

    def get_conversation_history(self):
        return self.session_state.messages