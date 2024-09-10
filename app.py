import streamlit as st
from chatbot import ChatBot
import logging

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
        padding-bottom: 3rem;
        max-width: 800px;
    }
    .sidebar .sidebar-content {
        background-color: #202123;
        color: white;
        padding: 1rem;
    }
    .sidebar .sidebar-content .block-container {
        padding-top: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #f7f7f8;
    }
    .chat-message.bot {
        background-color: #ffffff;
        border: 1px solid #d9d9e3;
    }
    .chat-message .avatar {
        width: 15%;
        margin-right: 1rem;
    }
    .chat-message .avatar img {
        max-width: 40px;
        max-height: 40px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-message .message {
        width: 85%;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border-radius: 0.375rem;
        border: 1px solid #d9d9e3;
        padding: 0.5rem 1rem;
        font-size: 1rem;
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
    .input-container {
        position: fixed;
        bottom: 0;
        left: 22%; /* Adjust based on your sidebar width */
        right: 0;
        padding: 1rem;
        background-color: #ffffff;
        z-index: 1000;
        display: flex;
        align-items: center;
    }
    .input-container > div:first-child {
        flex-grow: 1;
        margin-right: 0.5rem;
    }
    .chat-container {
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding-right: 1rem;
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
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I assist you with information about JKKN Educational Institutions today?"}
            ]
            st.rerun()

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you with information about JKKN Educational Institutions today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user"><div class="avatar"><img src="https://i.imgur.com/4KeKvtH.png"/></div><div class="message">{message["content"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot"><div class="avatar"><img src="https://i.imgur.com/p1thPfH.png"/></div><div class="message">{message["content"]}</div></div>', unsafe_allow_html=True)

    # User input
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("Type your message here...", key="user_input")
        with col2:
            send_button = st.button("Send")
        st.markdown('</div>', unsafe_allow_html=True)

        if send_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.process_user_input(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)
            
            st.rerun()

if __name__ == "__main__":
    main()