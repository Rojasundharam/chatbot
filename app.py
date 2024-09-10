import streamlit as st
from chatbot import ChatBot
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for green gradient theme and Gemini-style loading animation
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #a8e063, #56ab2f);
    }
    .stTextInput > div > div > input {
        background-color: #e8f5e9;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
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
    placeholder.markdown("""
    <div class="gemini-loader">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)  # Simulating response time
    placeholder.markdown(final_response)

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
            with st.chat_message(message["role"]):
                st.write(message["content"])

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