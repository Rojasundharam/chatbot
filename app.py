import streamlit as st
from chatbot import ChatBot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page configuration
st.set_page_config(page_title="JKKN Assist", page_icon="🎓", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {color: #1E3C72; font-size: 40px; font-weight: bold; margin-bottom: 20px;}
    .sub-header {font-size: 24px; color: #34495E; margin-bottom: 30px;}
    .chat-message {padding: 15px; border-radius: 15px; margin-bottom: 10px; line-height: 1.5;}
    .user-message {background-color: #E0E0E0; border-top-right-radius: 0;}
    .bot-message {background-color: #D4E6F1; border-top-left-radius: 0;}
    .sidebar-content {padding: 20px; background-color: #F0F8FF; border-radius: 10px; margin-bottom: 20px;}
    .stTextInput>div>div>input {font-size: 16px;}
    .stSpinner>div>div>div {border-top-color: #1E3C72;}
</style>
""", unsafe_allow_html=True)

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
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.markdown("### Chat History")
    
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {"Current Chat": st.session_state.messages}
    
    selected_chat = st.sidebar.selectbox("Select Chat", list(st.session_state.chat_sessions.keys()))
    
    if selected_chat:
        messages = st.session_state.chat_sessions[selected_chat]
        for i, message in enumerate(messages):
            if message["role"] == "user":
                st.sidebar.markdown(f"**You:**")
                st.sidebar.text_area("", value=message["content"], height=50, key=f"{selected_chat}_user_msg_{i}", disabled=True)
            else:
                st.sidebar.markdown(f"**JKKN Assist:**")
                st.sidebar.text_area("", value=message["content"], height=100, key=f"{selected_chat}_assistant_msg_{i}", disabled=True)
            st.sidebar.markdown("---")
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">JKKN Assist 🤖</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI assistant for JKKN Educational Institutions</p>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you with information about JKKN Educational Institutions today?"}
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

    # Sidebar controls
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.sidebar.button("New Chat"):
        chat_name = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[chat_name] = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        st.session_state.messages = st.session_state.chat_sessions[chat_name]
        st.experimental_rerun()

    if st.sidebar.button("Clear Current Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
        st.session_state.chat_sessions["Current Chat"] = st.session_state.messages
        st.experimental_rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Additional Information
    st.markdown("---")
    st.markdown("### About JKKN Assist")
    st.write("""
    JKKN Assist is an AI-powered chatbot designed to provide information about JKKN Educational Institutions. 
    It can answer questions about courses, admissions, facilities, and more. The information provided is based 
    on the latest available data from JKKN's official documents.
    """)
    st.markdown("### How to Use")
    st.write("""
    1. Type your question in the chat input box above.
    2. Press Enter to submit your question.
    3. Wait for JKKN Assist to process your query and provide a response.
    4. You can ask follow-up questions or start a new topic at any time.
    5. Use the sidebar to switch between different chat sessions or start a new one.
    """)

    # Feedback section
    st.markdown("### Feedback")
    st.write("We're constantly working to improve JKKN Assist. Your feedback is valuable to us!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("This was helpful"):
            st.success("Thank you for your positive feedback!")
    with col2:
        if st.button("I need more information"):
            st.info("We appreciate your feedback. We'll work on providing more comprehensive information in the future.")

if __name__ == "__main__":
    main()