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

def main():
    st.title("JKKN Assist 🤖")
    st.write("I'm here to help with information about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me about JKKN institutions"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = st.session_state.chatbot.process_user_input(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                st.error(error_msg)
                logging.error(error_msg)

    st.sidebar.title("Debug Info")
    if st.sidebar.button("Print Session State"):
        st.sidebar.write(st.session_state)
    if st.sidebar.button("Print Chatbot Info"):
        if "chatbot" in st.session_state:
            st.sidebar.write({
                "Documents loaded": len(st.session_state.chatbot.documents),
                "Embeddings created": len(st.session_state.chatbot.embeddings),
                "FAISS index size": st.session_state.chatbot.index.ntotal if st.session_state.chatbot.index else "N/A",
                "TF-IDF matrix shape": st.session_state.chatbot.tfidf_matrix.shape if st.session_state.chatbot.tfidf_matrix else "N/A"
            })
        else:
            st.sidebar.write("Chatbot not initialized")

if __name__ == "__main__":
    main()