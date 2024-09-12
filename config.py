import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Drive settings
GOOGLE_DRIVE_FOLDER_ID = "1EyR0sfFEBUDGbPn3lBDIP5qcFumItrvQ"
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Anthropic API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-2.1"

# Document indexing settings
UPDATE_INTERVAL = 600  # 10 minutes in seconds

# Embedding model settings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# QA model settings
QA_MODEL = "distilbert-base-cased-distilled-squad"

# Chatbot settings
MAX_TOKENS = 2048
TOP_K_DOCUMENTS = 3

# Streamlit settings
STREAMLIT_THEME_COLOR = "#56ab2f"