import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS

def main():
    st.title("JKKN Assist 🤖")

    # Initialize session state for messages and chatbot
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

    # Display chat history
    for message in st.session_state.messages:
        st.write(f"{message['role'].capitalize()}: {message['content']}")

    # Input field for the user's question
    user_msg = st.text_input("Type your question about JKKN institutions here...")

    if user_msg:
        # Add the user message and ensure assistant responds before adding a new user message
        st.session_state.messages.append({'role': 'user', 'content': user_msg})

        # Assistant's response processing
        full_response = st.session_state.chatbot.process_user_input(user_msg)
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})

        st.write(f"Assistant: {full_response}")

if __name__ == "__main__":
    main()
