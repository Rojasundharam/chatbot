import streamlit as st
from chatbot import ChatBot
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for a professional UI
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 0.5rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 1px #4CAF50;
    }
    .user-message {
        background-color: #e7f3fe;
        border-radius: 15px 15px 0 15px;
        padding: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #f0f0f0;
        border-radius: 15px 15px 15px 0;
        padding: 10px;
        margin: 5px 0;
        text-align: left;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #333;
        text-align: center;
        margin-bottom: 1rem;
    }
    .header {
        background-color: #4CAF50;
        color: white;
        padding: 1rem;
        border-radius: 10px 10px 0 0;
        margin-bottom: 1rem;
    }
    .header h1 {
        color: white;
        margin: 0;
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
    st.set_page_config(page_title="JKKN Assist", page_icon="🎓", layout="wide")
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown('<h1>JKKN Assist 🎓</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("Welcome to JKKN Assist. How can I help you today?")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not initialize_chatbot():
        st.stop()

    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("Type your question here", key="user_input")
    if st.button("Send"):
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Processing your request..."):
                try:
                    response = st.session_state.chatbot.process_user_input(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)
            
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()