import streamlit as st
import asyncio
import time
from chatbot import ChatBot, download_nltk_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
STREAMLIT_THEME_COLOR = "#56ab2f"  # You can adjust this color

st.set_page_config(page_title="JKKN Assist", page_icon="🤖", layout="wide")

# Custom CSS for green gradient theme
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(to bottom right, #a8e063, {STREAMLIT_THEME_COLOR});
    }}
    .stTextInput > div > div > input {{
        background-color: #e8f5e9;
    }}
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px;
        padding: 10px;
    }}
    .stChatMessageContent {{
        background-color: transparent !important;
    }}
    h1 {{
        color: #1b5e20;
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_chatbot():
    try:
        download_nltk_data()  # Ensure NLTK data is downloaded
        return ChatBot(st.session_state)
    except Exception as e:
        logging.error(f"Error initializing ChatBot: {str(e)}")
        st.error(f"Failed to initialize ChatBot: {str(e)}")
        return None

def initialize_chatbot():
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = get_chatbot()
    
    if st.session_state.chatbot is None:
        st.error("ChatBot initialization failed. Please check your environment and try again.")
        return False
    return True

async def process_user_input_wrapper(chatbot, prompt):
    try:
        return await chatbot.process_user_input_async(prompt)
    except Exception as e:
        logging.error(f"Error processing user input: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your request. Please try again later."

def main():
    st.title("JKKN Assist 🤖")
    st.write("Ask me anything about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Display last update time and indexed documents
    st.sidebar.subheader("Document Index Status")
    last_update = st.sidebar.empty()
    indexed_docs = st.sidebar.empty()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Use asyncio to run the asynchronous process_user_input_async
                response = asyncio.run(process_user_input_wrapper(st.session_state.chatbot, prompt))
                
                # Simulate streaming
                for chunk in response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                st.error("An error occurred while processing your request. Please try again or contact support if the problem persists.")

    # Update sidebar information
    last_update.text(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.chatbot.last_update_time))}")
    with st.sidebar.expander("Indexed documents"):
        for doc_name in st.session_state.chatbot.get_indexed_document_names():
            st.text(f"- {doc_name}")

if __name__ == "__main__":
    main()