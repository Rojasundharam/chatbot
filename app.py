import streamlit as st
from chatbot import ChatBot
import logging
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom CSS for layout and green input box
st.markdown("""
<style>
    .logo-text {
        font-size: 24px;
        font-weight: bold;
        margin-left: 10px;
        vertical-align: middle;
    }
    .logo-img {
        vertical-align: middle;
    }
    /* Green input box styles */
    .stTextInput > div > div > input {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 1px #4CAF50 !important;
    }
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 2px #45a049 !important;
    }
    /* Changing the color of the send button */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# ... [rest of your code remains the same]

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

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    response = st.session_state.chatbot.process_user_input(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    logging.error(error_msg)

if __name__ == "__main__":
    main()