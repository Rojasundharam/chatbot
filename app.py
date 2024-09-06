import streamlit as st
from chatbot import ChatBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def display_chat_history():
    st.sidebar.title("Chat History")
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.sidebar.markdown(f"**You:**")
            st.sidebar.text_area("", value=message["content"], height=50, key=f"user_msg_{i}", disabled=True)
        else:
            st.sidebar.markdown(f"**JKKN Assist:**")
            st.sidebar.text_area("", value=message["content"], height=100, key=f"assistant_msg_{i}", disabled=True)
        st.sidebar.markdown("---")

def main():
    st.title("JKKN Assist 🤖")
    st.write("I'm here to help with information about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Display chat history in the main area
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input for new messages
    if prompt := st.chat_input("Ask me about JKKN institutions"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.process_user_input(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

    # Display chat history in the sidebar
    display_chat_history()

    # Add a clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        st.experimental_rerun()

if __name__ == "__main__":
    main()