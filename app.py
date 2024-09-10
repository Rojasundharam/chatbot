import streamlit as st
from chatbot import ChatBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for improved UI
st.markdown("""
<style>
    .stApp {
        background-color: #e8f5e9;
    }
    .stHeader {
        background-color: #4CAF50;
        padding: 1rem;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
    }
    .stHeader h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 24px;
    }
    .chat-container {
        margin-top: 70px;
        margin-bottom: 70px;
        padding: 1rem;
        overflow-y: auto;
        height: calc(100vh - 140px);
    }
    .stTextInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: white;
        z-index: 1000;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 1px solid #4CAF50;
        padding-right: 40px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 1px #4CAF50;
    }
    .stTextInput > div > div::after {
        content: '➤';
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: #4CAF50;
        font-size: 20px;
    }
    .user-message {
        background-color: #DCF8C6;
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-end;
        float: right;
        clear: both;
    }
    .bot-message {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-start;
        float: left;
        clear: both;
    }
    div[data-testid="stVerticalBlock"] {
        padding-bottom: 70px;
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
    st.markdown('<div class="stHeader"><h1>JKKN Assist 🤖</h1></div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Create a container for chat messages
    chat_container = st.container()

    # Display chat history
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("Type your question here", key="user_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
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