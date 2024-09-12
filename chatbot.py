import asyncio
import time
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OptimizedDocumentRetrieval:
    def __init__(self, documents):
        self.documents = documents
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.document_embeddings = self.model.encode([doc['content'] for doc in self.documents])

    def get_similar_documents(self, query, k=2):
        query_embedding = self.model.encode([query])
        scores = np.dot(self.document_embeddings, query_embedding.T).flatten()
        top_indices = scores.argsort()[-k:][::-1]
        similar_docs = [self.documents[i] for i in top_indices]
        return similar_docs, scores[top_indices]

class ImprovedResponseGenerator:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.model.eval()

    def generate_response(self, query, context, max_length=150):
        input_text = f"Query: {query}\nContext: {context}\nResponse:"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids, 
                max_length=max_length, 
                num_return_sequences=1, 
                no_repeat_ngram_size=2, 
                top_k=50, 
                top_p=0.95, 
                temperature=0.7
            )
        
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return response.split("Response:")[-1].strip()

class ChatBot:
    def __init__(self, session_state):
        self.session_state = session_state
        self.documents = self.load_documents()
        self.document_retrieval = OptimizedDocumentRetrieval(self.documents)
        self.response_generator = ImprovedResponseGenerator()
        self.last_update_time = time.time()

    def load_documents(self):
        return [
            {"id": "1", "name": "JKKN Overview", "content": "JKKN Educational Institutions offer a wide range of programs including engineering, management, and health sciences. Founded in 1995, JKKN has become a leading educational group in the region."},
            {"id": "2", "name": "Admission Process", "content": "To apply for admission to JKKN, students need to follow these steps: 1) Fill out the online application form, 2) Submit required documents, 3) Pay the application fee, 4) Attend the entrance exam if required for the chosen program."},
            {"id": "3", "name": "Campus Facilities", "content": "JKKN campuses are equipped with state-of-the-art facilities including modern laboratories, libraries with extensive collections, sports complexes, and comfortable student housing. Wi-Fi is available throughout the campus."},
            {"id": "4", "name": "Faculty", "content": "JKKN boasts a highly qualified faculty with many holding PhDs from renowned universities. Our professors are dedicated to providing quality education and are actively involved in research and industry collaborations."},
            {"id": "5", "name": "Placements", "content": "JKKN has an excellent track record in placements. Our dedicated placement cell works tirelessly to ensure students get opportunities in top companies. Many of our alumni are working in Fortune 500 companies."}
        ]

    async def process_user_input_async(self, user_input):
        try:
            similar_docs, scores = self.document_retrieval.get_similar_documents(user_input)
            context = "\n".join([doc['content'] for doc in similar_docs])
            response = self.response_generator.generate_response(user_input, context)
            return response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Please try again later."

    def get_indexed_document_names(self):
        return [doc['name'] for doc in self.documents]