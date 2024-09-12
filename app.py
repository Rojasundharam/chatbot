import streamlit as st
from chatbot import ChatBot
import logging
import time
from config import STREAMLIT_THEME_COLOR
import cProfile
import pstats
import io
import torch
from transformers import BertTokenizer, BertModel
import nltk
from nltk.corpus import wordnet

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

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
def load_bert_model():
    model = BertModel.from_pretrained('bert-base-uncased')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    return model, device, tokenizer

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

def query_rewrite(query):
    # Tokenize the query
    tokens = nltk.word_tokenize(query.lower())
    
    # Perform part-of-speech tagging
    pos_tags = nltk.pos_tag(tokens)
    
    # Expand query with synonyms for nouns and verbs
    expanded_tokens = []
    for token, pos in pos_tags:
        expanded_tokens.append(token)
        if pos.startswith('N') or pos.startswith('V'):  # Nouns or Verbs
            synsets = wordnet.synsets(token)
            for synset in synsets[:2]:  # Take up to 2 synonyms
                for lemma in synset.lemmas():
                    if lemma.name() != token:
                        expanded_tokens.append(lemma.name())
    
    # Join the expanded tokens back into a query
    expanded_query = ' '.join(expanded_tokens)
    
    # Add JKKN-specific terms if they're not already in the query
    jkkn_terms = ['jkkn', 'education', 'institution', 'college', 'university']
    for term in jkkn_terms:
        if term not in expanded_query:
            expanded_query += f' {term}'
    
    return expanded_query

def process_user_input(prompt, model, device, tokenizer):
    pr = cProfile.Profile()
    pr.enable()

    # Use the BERT model for query rewriting
    with torch.no_grad():
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    
    chatbot = st.session_state.chatbot
    
    # Rewrite the query
    rewritten_query = query_rewrite(prompt)
    
    # Process the rewritten query
    response = chatbot.process_user_input(rewritten_query)
    similar_docs, scores = chatbot.get_similar_documents(rewritten_query)

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()

    logging.info(f"Performance profile:\n{s.getvalue()}")

    return response, similar_docs, scores

def handle_greeting(name):
    return f"Hello {name}! Welcome to JKKN Assist. How can I help you with information about JKKN Educational Institutions today?"

def handle_general_query():
    return ("JKKN is a group of educational institutions. Would you like to know about its history, programs, or any specific aspect of JKKN? Please feel free to ask more specific questions.")

def main():
    st.title("JKKN Assist 🤖")
    st.write("Ask me anything about JKKN Educational Institutions.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    if not initialize_chatbot():
        st.stop()

    # Load BERT model
    model, device, tokenizer = load_bert_model()

    # Display last update time and indexed documents
    st.sidebar.subheader("Document Index Status")
    last_update = st.sidebar.empty()
    indexed_docs = st.sidebar.empty()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Check for greetings or general queries
            if prompt.lower().startswith(("hello", "hi", "hey")):
                response = "Hello! How can I assist you with information about JKKN Educational Institutions today?"
            elif "i am" in prompt.lower():
                name = prompt.lower().split("i am")[-1].strip()
                response = handle_greeting(name)
            elif prompt.lower() in ["do you know jkkn", "what is jkkn", "tell me about jkkn"]:
                response = handle_general_query()
            else:
                response, similar_docs, scores = process_user_input(prompt, model, device, tokenizer)
            
            for chunk in response.split():  # Simulate streaming response
                full_response += chunk + " "
                time.sleep(0.05)  # Add a small delay for a more natural effect
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Display top document matches
            if 'similar_docs' in locals() and similar_docs:
                with st.expander("Top Matching Documents"):
                    for doc, score in zip(similar_docs, scores):
                        st.markdown(f"- [{doc['name']}](https://drive.google.com/file/d/{doc['id']}/view) (Relevance: {score:.2f})")
            else:
                st.info("No closely matching documents found for this query.")

    # Update sidebar information
    last_update.text(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.chatbot.last_update_time))}")
    with st.sidebar.expander("Indexed documents"):
        for doc_name in st.session_state.chatbot.get_indexed_document_names():
            st.text(f"- {doc_name}")

if __name__ == "__main__":
    main()