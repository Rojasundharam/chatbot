import os
from dotenv import load_dotenv
from anthropic import Anthropic
from config import IDENTITY, TOOLS, MODEL, RAG_PROMPT
from google_drive_utils import get_drive_service, get_documents, get_document_content
from embedding_utils import EmbeddingUtil
import logging

load_dotenv()

class ChatBot:
    def __init__(self, session_state):
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

    def load_documents(self):
        files = get_documents(self.drive_service, self.folder_id)
        documents = []
        for file in files:
            content = get_document_content(self.drive_service, file['id'])
            documents.append(content)
            logging.info(f"Loaded document: {file['name']}")
        return documents

    def get_relevant_context(self, query, max_tokens=100000):
        similar_indices = self.embedding_util.search_similar(query, self.index, self.embeddings)
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

    def process_user_input(self, user_input):
        context = self.get_relevant_context(user_input)
        rag_message = RAG_PROMPT.format(context=context, question=user_input)
        
        messages_for_api = [
            {"role": "user", "content": rag_message}
        ]

        try:
            response_message = self.generate_message(messages_for_api)
            assistant_response = response_message.content[0].text
            return assistant_response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            raise

    def get_conversation_history(self):
        return self.session_state.messages