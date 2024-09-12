import time
import threading
import logging
import re
from google_drive_utils import get_drive_service, index_documents
from embedding_utils import EmbeddingUtil
from anthropic import Anthropic
from transformers import pipeline
from config import (
    GOOGLE_DRIVE_FOLDER_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    UPDATE_INTERVAL,
    EMBEDDING_MODEL,
    QA_MODEL,
    MAX_TOKENS,
    TOP_K_DOCUMENTS
)

class ChatBot:
    def __init__(self, session_state):
        self.session_state = session_state
        
        if not GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        
        self.drive_service = get_drive_service()
        self.folder_id = GOOGLE_DRIVE_FOLDER_ID
        
        self.embedding_util = EmbeddingUtil()
        
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        self.qa_model = pipeline("question-answering", model=QA_MODEL)
        
        self.documents = []
        self.last_update_time = 0
        self.update_interval = UPDATE_INTERVAL
        self.update_lock = threading.Lock()
        
        self.cache = {}
        
        # Initialize documents and index
        self.update_documents()
        
        # Start the background update thread
        self.update_thread = threading.Thread(target=self.background_update, daemon=True)
        self.update_thread.start()

    def background_update(self):
        while True:
            time.sleep(self.update_interval)
            with self.update_lock:
                self.update_documents()

    def update_documents(self):
        try:
            new_documents = index_documents(self.drive_service, self.folder_id)
            if new_documents:
                new_texts = [doc['content'] for doc in new_documents if doc['id'] not in [d['id'] for d in self.documents]]
                new_doc_ids = [doc['id'] for doc in new_documents if doc['id'] not in [d['id'] for d in self.documents]]
                if new_texts:
                    self.embedding_util.update_index(new_texts, new_doc_ids)
                self.documents = new_documents
                print(f"Updated {len(self.documents)} documents")
            else:
                print("No new documents found")
        except Exception as e:
            print(f"Error updating documents: {str(e)}")

    def get_similar_documents(self, query, k=TOP_K_DOCUMENTS):
        similar_doc_ids, scores = self.embedding_util.search_similar(query, k=k)
        if not similar_doc_ids:
            return [], []
        return [doc for doc in self.documents if doc['id'] in similar_doc_ids], scores

    def process_user_input(self, user_input: str) -> str:
        if self.is_greeting(user_input):
            return "Hello! How can I assist you with information about JKKN Educational Institutions today?"

        # Check cache
        if user_input in self.cache:
            return self.cache[user_input]

        try:
            similar_docs, scores = self.get_similar_documents(user_input)
            if not similar_docs:
                return "I'm sorry, but I don't have any information to answer your question at the moment. Please try again later or ask a different question."

            context = "\n\n".join([doc['content'] for doc in similar_docs])

            # Early stopping
            if scores and scores[0] > 0.9:  # Adjust this threshold as needed
                context = similar_docs[0]['content']
            
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
            5. If the user's question is not specific or cannot be answered with the given context, politely ask for clarification.

            Answer:
            """

            response_message = self.generate_message([{"role": "user", "content": rag_message}])
            assistant_response = response_message.content[0].text

            # Cache the response
            self.cache[user_input] = assistant_response

            return assistant_response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question about JKKN institutions?"

    def is_greeting(self, text):
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        return any(re.search(rf'\b{greeting}\b', text.lower()) for greeting in greetings)

    def extract_answer(self, question, context):
        if not context:
            return "I'm sorry, but I don't have enough information to answer that question accurately."
        result = self.qa_model(question=question, context=context)
        return result['answer']

    def generate_message(self, messages, max_tokens=MAX_TOKENS):
        try:
            response = self.anthropic.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                messages=messages
            )
            return response
        except Exception as e:
            logging.error(f"Error generating message: {str(e)}")
            raise

    def get_indexed_document_names(self):
        return [doc['name'] for doc in self.documents]

    def query_rewrite(self, query):
        # Simple query rewriting rules
        query = query.lower()
        query = re.sub(r'\bwhats\b', 'what is', query)
        query = re.sub(r'\bhows\b', 'how is', query)
        query = re.sub(r'\bwheres\b', 'where is', query)
        query = re.sub(r'\bwhos\b', 'who is', query)
        return query