import streamlit as st
from chatbot import ChatBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for the UI
st.markdown("""
<style>
    .stApp {
        background-color: #e8f5e9;
    }
    .header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #4CAF50;
        color: white;
        text-align: center;
        padding: 1rem;
        z-index: 1000;
    }
    .chat-container {
        margin-top: 5rem;
        margin-bottom: 5rem;
        padding: 1rem;
        overflow-y: auto;
        height: calc(100vh - 10rem);
    }
    .message-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem;
        background-color: white;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .stButton > button {
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
    }
    .user-message {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: left;
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
    st.markdown('<div class="header"><h1>Career Path Advisor</h1></div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not initialize_chatbot():
        st.stop()

    chat_container = st.container()

    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="message-input">', unsafe_allow_html=True)
    user_input = st.text_input("Type your message here...", key="user_input")
    send_button = st.button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

    if send_button and user_input:
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