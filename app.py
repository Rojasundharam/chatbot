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
    
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {"Current Chat": st.session_state.messages}

    for chat_name, messages in st.session_state.chat_sessions.items():
        if st.sidebar.checkbox(chat_name):
            for i, message in enumerate(messages):
                if message["role"] == "user":
                    st.sidebar.markdown(f"**You:**")
                    st.sidebar.text_area("", value=message["content"], height=50, key=f"{chat_name}_user_msg_{i}", disabled=True)
                else:
                    st.sidebar.markdown(f"**JKKN Assist:**")
                    st.sidebar.text_area("", value=message["content"], height=100, key=f"{chat_name}_assistant_msg_{i}", disabled=True)
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

    # Add a new chat button
    if st.sidebar.button("New Chat"):
        chat_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[chat_name] = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        st.session_state.messages = st.session_state.chat_sessions[chat_name]
        st.experimental_rerun()

    # Add a clear chat button
    if st.sidebar.button("Clear Current Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        st.session_state.chat_sessions["Current Chat"] = st.session_state.messages
        st.experimental_rerun()

if __name__ == "__main__":
    main()