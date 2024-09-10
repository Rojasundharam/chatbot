import streamlit as st
from chatbot import ChatBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for green gradient theme with header, body, and footer
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom right, #a8e063, #56ab2f);
    }
    .header {
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .body {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
        padding: 10px;
    }
    .stTextInput > div > div > input {
        background-color: #e8f5e9;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessageContent {
        background-color: transparent !important;
    }
    h1 {
        color: #1b5e20;
        text-align: center;
    }
    .user-avatar {
        background-color: #4CAF50;
    }
    .bot-avatar {
        background-color: #1b5e20;
    }
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

def main():
    # Header
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.title("JKKN Assist 🤖")
    st.write("Your AI assistant for JKKN Educational Institutions")
    st.markdown('</div>', unsafe_allow_html=True)

    # Body
    st.markdown('<div class="body">', unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=f"{message['role']}-avatar"):
            st.write(message["content"])

    # User input
    prompt = st.chat_input("Type your question here")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="user-avatar"):
            st.write(prompt)
        
        with st.chat_message("assistant", avatar="bot-avatar"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.process_user_input(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2024 JKKN Educational Institutions. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()