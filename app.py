import streamlit as st
from chatbot import ChatBot
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for a more professional theme
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .stChatMessageContent {
        background-color: transparent !important;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #2c5282;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #1e3a8a;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
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

def get_current_time():
    return datetime.now().strftime("%H:%M")

def start_new_chat():
    st.session_state.messages = [
        {"role": "assistant", "content": "Starting a new chat. How can I help you today?", "time": get_current_time()}
    ]

def main():
    st.title("JKKN Assist 🎓")
    st.write("Welcome to your personal assistant for JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you with information about JKKN Educational Institutions today?", "time": get_current_time()}
        ]

    if not initialize_chatbot():
        st.stop()

    # New Chat button
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("New Chat"):
            start_new_chat()
            st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(f"{message['content']} - {message['time']}")

    # User input
    if prompt := st.chat_input("Type your question here..."):
        current_time = get_current_time()
        st.session_state.messages.append({"role": "user", "content": prompt, "time": current_time})
        with st.chat_message("user"):
            st.write(f"{prompt} - {current_time}")
        
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    response = st.session_state.chatbot.process_user_input(prompt)
                    current_time = get_current_time()
                    st.write(f"{response} - {current_time}")
                    st.session_state.messages.append({"role": "assistant", "content": response, "time": current_time})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

    # Footer
    st.markdown(
        """
        <div class="footer">
            JKKN Assist v1.0 | © 2024 JKKN Educational Institutions | 
            <a href="https://www.jkkn.edu.in" target="_blank">Visit our website</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()