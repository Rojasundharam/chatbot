import streamlit as st
from chatbot import ChatBot
import logging
from PIL import Image

# [Previous code remains the same]

def main():
    # Load and display logo
    logo = Image.open("jkkn_logo.png")  # Replace with your actual logo file name
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo, width=50, output_format="PNG")
    with col2:
        st.markdown('<p class="logo-text">JKKN ASSIST</p>', unsafe_allow_html=True)
    
    st.write("Welcome to your personal assistant for JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you with information about JKKN Educational Institutions today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Sidebar with New Chat button and logo
    with st.sidebar:
        st.image(logo, width=100, output_format="PNG")
        st.title("JKKN ASSIST")
        if st.button("New Chat"):
            start_new_chat()
            st.rerun()

    # Create a container for chat history
    chat_container = st.container()

    # User input
    user_input = st.text_input("Type your question here...", key="user_input")

    # Process user input and update chat history
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Processing your request..."):
            try:
                response = st.session_state.chatbot.process_user_input(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                st.error(error_msg)
                logging.error(error_msg)
        
        # Clear the input box after processing
        st.session_state.user_input = ""

    # Display chat history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

if __name__ == "__main__":
    main()