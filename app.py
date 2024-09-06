import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS
import logging

logging.basicConfig(level=logging.INFO)

def main():
    st.title("JKKN Assist 🤖")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {'role': "user", "content": TASK_SPECIFIC_INSTRUCTIONS},
            {'role': "assistant", "content": "Understood, I'm ready to assist with inquiries about JKKN Educational Institutions."},
        ]
    
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(st.session_state)
        except ValueError as e:
            st.error(f"Error initializing chatbot: {str(e)}")
            return

    for message in st.session_state.messages:
        st.write(f"{message['role'].capitalize()}: {message['content']}")

    user_msg = st.text_input("Type your question about JKKN institutions here...")

    if user_msg:
        try:
            full_response = st.session_state.chatbot.process_user_input(user_msg)
            st.write(f"Assistant: {full_response}")
        except ValueError as e:
            st.error(f"Error: {str(e)}")
            logging.error(f"ValueError in processing user input: {str(e)}")
        except Exception as e:
            st.error("An unexpected error occurred. Please try again with a shorter or simpler question.")
            logging.error(f"Unexpected error in processing user input: {str(e)}")

if __name__ == "__main__":
    main()