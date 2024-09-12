import streamlit as st
from chatbot import ChatBot
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for green gradient theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #a8e063, #56ab2f);
    }
    .stTextInput > div > div > input {
        background-color: #e8f5e9;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px;
        padding: 10px;
    }
    .stChatMessageContent {
        background-color: transparent !important;
    }
    h1 {
        color: #1b5e20;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatBot(st.session_state)
            logging.info("ChatBot initialized successfully")
        except ValueError as e:
            st.error(f"Failed to initialize ChatBot: {str(e)}")
            st.error("Please check your environment variables and Google Drive connection.")
            return False
        except Exception as e:
            logging.error(f"Unexpected error initializing ChatBot: {str(e)}")
            st.error(f"An unexpected error occurred: {str(e)}")
            return False
    return True

def main():
    st.title("JKKN Assist 🤖")
    st.write("Ask me anything about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Display last update time and indexed documents
    st.sidebar.subheader("Document Index Status")
    last_update = st.sidebar.empty()
    indexed_docs = st.sidebar.empty()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Type your question here"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.process_user_input(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Display top document matches
                    st.subheader("Top Matching Documents:")
                    similar_docs = st.session_state.chatbot.get_similar_documents(prompt, k=3)
                    for doc in similar_docs:
                        st.write(f"- {doc['name']}")
                        st.write(f"  Link: https://drive.google.com/file/d/{doc['id']}/view")

                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

    # Update sidebar information
    while True:
        last_update.text(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.chatbot.last_update_time))}")
        indexed_docs.text("Indexed documents:")
        for doc_name in st.session_state.chatbot.get_indexed_document_names():
            indexed_docs.text(f"- {doc_name}")
        time.sleep(60)  # Update every minute

if __name__ == "__main__":
    main()