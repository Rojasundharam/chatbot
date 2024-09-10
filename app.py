import streamlit as st
from chatbot import ChatBot
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for green theme matching the image
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
    }
    .chat-container {
        margin-top: 60px;
        margin-bottom: 60px;
        padding: 1rem;
        overflow-y: auto;
        height: calc(100vh - 120px);
    }
    .stTextInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: white;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessageContent {
        background-color: transparent !important;
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

def simulate_typing(placeholder, final_response):
    placeholder.markdown('<span class="typing-animation">Typing</span>', unsafe_allow_html=True)
    time.sleep(1)  # Simulating typing time
    placeholder.markdown(final_response)

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
            with st.chat_message(message["role"]):
                st.write(message["content"])
        st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.chat_input("Type your question here")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                try:
                    response = st.session_state.chatbot.process_user_input(user_input)
                    simulate_typing(response_placeholder, response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

if __name__ == "__main__":
    main()