import os
from dotenv import load_dotenv
from anthropic import Anthropic
from config import IDENTITY, TOOLS, MODEL, RAG_PROMPT
from google_drive_utils import get_drive_service, get_documents, get_document_content
from embedding_utils import EmbeddingUtil
import logging

# Load environment variables from .env file
load_dotenv()

class ChatBot:
    def __init__(self, session_state):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Anthropic client initialization
        self.anthropic = Anthropic(api_key=api_key)
        self.session_state = session_state
        self.drive_service = get_drive_service()
        self.folder_id = "1EyR0sfFEBUDGbPn3lBDIP5qcFumItrvQ"  # Your folder ID
        self.documents = self.load_documents()
        self.embedding_util = EmbeddingUtil()
        self.embeddings = self.embedding_util.create_embeddings(self.documents)
        self.index = self.embedding_util.create_faiss_index(self.embeddings)

    def load_documents(self):
        """Load documents from Google Drive."""
        files = get_documents(self.drive_service, self.folder_id)
        documents = []
        for file in files:
            content = get_document_content(self.drive_service, file['id'])
            documents.append(content)
            logging.info(f"Loaded document: {file['name']}")
        return documents

    def get_relevant_context(self, query):
        """Find relevant document context using FAISS index."""
        similar_indices = self.embedding_util.search_similar(query, self.index, self.embeddings)
        context = "\n".join([self.documents[i] for i in similar_indices])
        return context

    def generate_message(self, messages, max_tokens=2048):
        """Generate a message using the Anthropic API."""
        response = self.anthropic.messages.create(
            model=MODEL,
            system=IDENTITY,
            max_tokens=max_tokens,
            messages=messages,
            tools=TOOLS,
        )
        return response

    def process_user_input(self, user_input):
        """Process user input and return the AI's response."""
        
        # Ensure that messages alternate correctly
        if self.session_state.messages[-1]['role'] != "assistant":
            raise ValueError("Multiple 'user' messages detected in a row. Assistant must respond before the next user message.")

        # Retrieve context based on the query
        context = self.get_relevant_context(user_input)
        rag_message = RAG_PROMPT.format(context=context, question=user_input)
        
        # Append the user message
        self.session_state.messages.append({"role": "user", "content": rag_message})
        
        # Generate a response from the assistant
        response_message = self.generate_message(self.session_state.messages)
        if "error" in response_message:
            return f"An error occurred: {response_message['error']}"

        assistant_response = response_message.content[0].text
        # Append the assistant message
        self.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response
