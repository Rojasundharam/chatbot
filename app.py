import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS
import logging

logging.basicConfig(level=logging.INFO)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {'role': "assistant", "content": "Hello! I'm JKKN Assist, here to help you with information about JKKN Educational Institutions. How may I assist you today?"}
        ]
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(st.session_state)
        except ValueError as e:
            st.error(f"Error initializing chatbot: {str(e)}")

def display_conversation_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input():
    user_input = st.chat_input("Type your question about JKKN institutions here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                for response_chunk in st.session_state.chatbot.process_user_input(user_input):
                    full_response += response_chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_message = "I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question or asking about a different topic related to JKKN institutions?"
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                logging.error(f"Error processing user input: {str(e)}")

def main():
    st.title("JKKN Assist 🤖")
    st.caption("I'm here to help with information about JKKN Educational Institutions. Ask me about courses, admissions, facilities, or any other aspect of our institutions!")
    
    initialize_session_state()
    display_conversation_history()
    handle_user_input()

    # Add a feedback section
    st.sidebar.title("Feedback")
    if st.sidebar.button("This response was helpful"):
        st.sidebar.success("Thank you for your feedback!")
    if st.sidebar.button("This response was not helpful"):
        st.sidebar.error("We're sorry the response wasn't helpful. We'll work on improving it.")

if __name__ == "__main__":
    main()