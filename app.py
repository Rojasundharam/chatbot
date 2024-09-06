import streamlit as st
from chatbot import ChatBot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm JKKN Assist. How can I help you today?"}
        ]
    
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(st.session_state)
            logging.info("ChatBot initialized successfully")
        except Exception as e:
            error_msg = f"Error initializing chatbot: {str(e)}"
            st.error(error_msg)
            logging.error(error_msg)
            st.stop()

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
                full_response = st.session_state.chatbot.process_user_input(user_input)
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_message = "I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question or asking about a different topic?"
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                logging.error(f"Error processing user input: {str(e)}")

def main():
    st.set_page_config(page_title="JKKN Assist", page_icon="🤖", layout="centered")
    
    st.title("JKKN Assist 🤖")
    st.caption("I'm here to help with information about JKKN Educational Institutions. Ask me about courses, admissions, facilities, or any other aspect of our institutions!")
    
    logging.info("Starting main function")
    
    initialize_session_state()
    logging.info(f"Session state initialized: {st.session_state.keys()}")
    
    display_conversation_history()
    logging.info("Conversation history displayed")
    
    handle_user_input()
    logging.info("User input handled")

    # Add a feedback section
    st.sidebar.title("Feedback")
    if st.sidebar.button("This response was helpful"):
        st.sidebar.success("Thank you for your feedback!")
        logging.info("Positive feedback received")
    if st.sidebar.button("This response was not helpful"):
        st.sidebar.error("We're sorry the response wasn't helpful. We'll work on improving it.")
        logging.info("Negative feedback received")

if __name__ == "__main__":
    main()