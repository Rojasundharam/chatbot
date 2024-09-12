import streamlit as st
from chatbot import ChatBot
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            st.error("Please check your environment variables and Elasticsearch connection.")
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
                    similar_doc_ids = st.session_state.chatbot.embedding_util.search_similar(prompt, k=3)
                    for doc_id in similar_doc_ids:
                        doc = st.session_state.chatbot.es.get(index="jkkn_documents", id=doc_id)
                        st.write(f"- {doc['_source']['name']}")
                        st.write(f"  Link: https://drive.google.com/file/d/{doc_id}/view")

                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

if __name__ == "__main__":
    main()