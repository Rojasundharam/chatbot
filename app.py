import streamlit as st
from chatbot import ChatBot
import logging
import time

# Set page config at the very beginning
st.set_page_config(page_title="JKKN Assist", page_icon="🎓", layout="wide")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for ChatGPT-like UI
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #202123;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #f7f7f8;
    }
    .chat-message.bot {
        background-color: #ffffff;
        border: 1px solid #d9d9e3;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .avatar img {
        max-width: 78px;
        max-height: 78px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-message .message {
        width: 80%;
        padding: 0 1.5rem;
    }
    input {
        border-radius: 0.375rem;
        border: 1px solid #d9d9e3;
    }
    .stButton > button {
        background-color: #19c37d;
        color: white;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #0f9c5d;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(st.session_state)
            logging.info("ChatBot initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ChatBot: {str(e)}")
            st.error(f"Failed to initialize ChatBot: {str(e)}")
            return False
    return True

def main():
    # Sidebar
    with st.sidebar:
        st.title("JKKN Assist 🎓")
        st.markdown("Welcome to JKKN Assist. How can I help you today?")
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.experimental_rerun()

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not initialize_chatbot():
        st.stop()

    # Display chat messages
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user"><div class="avatar"><img src="https://i.imgur.com/4KeKvtH.png"/></div><div class="message">{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot"><div class="avatar"><img src="https://i.imgur.com/p1thPfH.png"/></div><div class="message">{message["content"]}</div></div>', unsafe_allow_html=True)

    # User input
    with st.container():
        user_input = st.text_input("Type your message here...", key="user_input")
        if st.button("Send"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chatbot.process_user_input(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error processing request: {str(e)}"
                        st.error(error_msg)
                        logging.error(error_msg)
                
                st.experimental_rerun()

if __name__ == "__main__":
    main()