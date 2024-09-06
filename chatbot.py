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
        response = self.anthropic.messages.create(
            model=MODEL,
            system=IDENTITY,
            max_tokens=max_tokens,
            messages=messages,
            tools=TOOLS,
        )
        return response

    def validate_message_history(self, messages):
        if len(messages) < 2:
            return True  # Not enough messages to cause an issue
        for i in range(1, len(messages)):
            if messages[i]['role'] == messages[i-1]['role']:
                return False  # Found consecutive messages with the same role
        return True

    def process_user_input(self, user_input):
        if self.session_state.messages[-1]['role'] == "user":
            raise ValueError("Multiple 'user' messages detected in a row. Assistant must respond before the next user message.")

        context = self.get_relevant_context(user_input)
        rag_message = RAG_PROMPT.format(context=context, question=user_input)
        
        # Count tokens in the entire input
        total_tokens = self.anthropic.count_tokens(rag_message) + sum(self.anthropic.count_tokens(msg['content']) for msg in self.session_state.messages)
        
        if total_tokens > 190000:  # Leave some buffer
            logging.warning(f"Input too long: {total_tokens} tokens. Truncating context.")
            context = self.get_relevant_context(user_input, max_tokens=50000)  # Adjust as needed
            rag_message = RAG_PROMPT.format(context=context, question=user_input)

        self.session_state.messages.append({"role": "user", "content": rag_message})

        if not self.validate_message_history(self.session_state.messages):
            raise ValueError("Invalid message history: roles must alternate between user and assistant")

        try:
            response_message = self.generate_message(self.session_state.messages)
            assistant_response = response_message.content[0].text
            self.session_state.messages.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            logging.error(f"Error generating message: {str(e)}")
            raise