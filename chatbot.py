import os
import logging
from google_drive_utils import get_drive_service, index_documents
from embedding_utils import EmbeddingUtil
from elasticsearch import Elasticsearch
from anthropic import Anthropic
from transformers import pipeline

class ChatBot:
    def __init__(self, session_state):
        self.session_state = session_state
        self.drive_service = get_drive_service()
        self.folder_id = "1EyR0sfFEBUDGbPn3lBDIP5qcFumItrvQ"  # Your Google Drive folder ID
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.embedding_util = EmbeddingUtil()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        
        self.index_and_vectorize_documents()

    def index_and_vectorize_documents(self):
        index_documents(self.drive_service, self.folder_id)
        documents = self.es.search(index="jkkn_documents", body={"query": {"match_all": {}}}, size=1000)
        texts = [doc['_source']['content'] for doc in documents['hits']['hits']]
        doc_ids = [doc['_id'] for doc in documents['hits']['hits']]
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
        documents = self.es.mget(index="jkkn_documents", body={"ids": doc_ids})
        relevant_docs = [doc['_source']['content'] for doc in documents['docs'] if doc['found']]
        return "\n\n".join(relevant_docs)

    def extract_answer(self, question, context):
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