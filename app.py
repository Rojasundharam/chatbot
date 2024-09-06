import streamlit as st
from chatbot import ChatBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    st.title("JKKN Assist 🤖")
    st.write("I'm here to help with information about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me about JKKN institutions"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = f"You asked: {prompt}\nThis is a placeholder response."
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.sidebar.title("Debug Info")
    if st.sidebar.button("Print Session State"):
        st.sidebar.write(st.session_state)

if __name__ == "__main__":
    main()