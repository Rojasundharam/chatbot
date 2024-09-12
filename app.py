import streamlit as st
from chatbot import ChatBot
import logging
import time
from config import STREAMLIT_THEME_COLOR
import cProfile
import pstats
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for green gradient theme
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(to bottom right, #a8e063, {STREAMLIT_THEME_COLOR});
    }}
    .stTextInput > div > div > input {{
        background-color: #e8f5e9;
    }}
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px;
        padding: 10px;
    }}
    .stChatMessageContent {{
        background-color: transparent !important;
    }}
    h1 {{
        color: #1b5e20;
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_chatbot():
    return ChatBot(st.session_state)

def initialize_chatbot():
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = get_chatbot()
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

def process_user_input(chatbot, prompt):
    pr = cProfile.Profile()
    pr.enable()

    response = chatbot.process_user_input(chatbot.query_rewrite(prompt))
    similar_docs, scores = chatbot.get_similar_documents(prompt)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()

    logging.info(f"Performance profile:\n{s.getvalue()}")

    return response, similar_docs, scores

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
                    response, similar_docs, scores = process_user_input(st.session_state.chatbot, prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Display top document matches
                    if similar_docs:
                        st.subheader("Top Matching Documents:")
                        for doc, score in zip(similar_docs, scores):
                            st.write(f"- {doc['name']} (Relevance: {score:.2f})")
                            st.write(f"  Link: https://drive.google.com/file/d/{doc['id']}/view")
                    else:
                        st.info("No closely matching documents found for this query.")

                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

    # Update sidebar information
    last_update.text(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.chatbot.last_update_time))}")
    indexed_docs.text("Indexed documents:")
    for doc_name in st.session_state.chatbot.get_indexed_document_names():
        indexed_docs.text(f"- {doc_name}")

if __name__ == "__main__":
    main()