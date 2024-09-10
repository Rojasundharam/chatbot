import streamlit as st
from chatbot import ChatBot
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for refined green gradient theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #a8e063, #56ab2f);
    }
    .stTextInput > div > div > input {
        background-color: #e8f5e9;
        border: 2px solid #4CAF50 !important;
        border-radius: 20px;
        padding-left: 15px;
        color: #1b5e20;
    }
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 2px #4CAF50;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 2px solid #4CAF50 !important;
    }
    .stChatMessageContent {
        background-color: transparent !important;
    }
    h1 {
        color: #1b5e20;
        text-align: center;
    }
    .gemini-loader {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 40px;
    }
    .gemini-loader .dot {
        width: 10px;
        height: 10px;
        margin: 0 5px;
        background-color: #4CAF50;
        border-radius: 50%;
        opacity: 0;
        animation: pulse 1.5s ease-in-out infinite;
    }
    .gemini-loader .dot:nth-child(2) {
        animation-delay: 0.5s;
    }
    .gemini-loader .dot:nth-child(3) {
        animation-delay: 1s;
    }
    @keyframes pulse {
        0%, 100% { opacity: 0; transform: scale(0.5); }
        50% { opacity: 1; transform: scale(1); }
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
    }
    .stButton > button:hover {
        background-color: #45a049;
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

def display_loading_animation():
    return """
    <div class="gemini-loader">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
    """

def main():
    st.title("JKKN Assist 🤖")
    st.write("Ask me anything about JKKN Educational Institutions.")

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
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
                st.write(message["content"])

    # User input
    user_input = st.chat_input("Type your question here")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user", avatar="🧑"):
                st.write(user_input)
            
            with st.chat_message("assistant", avatar="🤖"):
                loading_placeholder = st.empty()
                loading_placeholder.markdown(display_loading_animation(), unsafe_allow_html=True)
                try:
                    response = st.session_state.chatbot.process_user_input(user_input)
                    time.sleep(1)  # Simulating response time
                    loading_placeholder.empty()
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    loading_placeholder.empty()
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

if __name__ == "__main__":
    main()