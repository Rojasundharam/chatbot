import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS
from google_drive_utils import get_drive_service

def main():
    st.title("JKKN Assist 🤖")

    # Initialize Google Drive authentication
    drive_service = get_drive_service()
    
    if drive_service is None:
        st.write("Please authenticate with Google Drive to continue.")
        return

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
            st.info("Please ensure the ANTHROPIC_API_KEY is correctly set in your .env file.")
            return

    # Display chat history (skipping initial instruction messages)
    for message in st.session_state.messages[2:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for the user's question
    if user_msg := st.chat_input("Type your question about JKKN institutions here..."):
        st.session_state.messages.append({'role': 'user', 'content': user_msg})
        st.chat_message("user").markdown(user_msg)

        # Assistant's response processing
        with st.chat_message("assistant"):
            with st.spinner("JKKN Assist is thinking..."):
                response_placeholder = st.empty()
                try:
                    # Process user input through the chatbot and append the response
                    full_response = st.session_state.chatbot.process_user_input(user_msg)
                    st.session_state.messages.append({'role': 'assistant', 'content': full_response})
                    response_placeholder.markdown(full_response)
                except Exception as e:
                    st.error(f"Error processing response: {str(e)}")

if __name__ == "__main__":
    main()
