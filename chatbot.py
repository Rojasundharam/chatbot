import asyncio
import time
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging
from cache import Cache
from web_scraper import scrape_webpage

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
        self.cache = Cache()
        self.web_sources = [
            "https://www.jkkn.org/about-us",
            "https://www.jkkn.org/courses",
            # Add more relevant URLs
        ]
        self.load_web_sources()

    def load_documents(self):
        # This is a placeholder implementation. In a real scenario, you'd load documents from a database or file system.
        return [
            {"id": "1", "name": "About JKKN", "content": "JKKN Educational Institutions offer a wide range of programs including engineering, management, and health sciences."},
            {"id": "2", "name": "Courses", "content": "JKKN offers various undergraduate and postgraduate courses in engineering, management, and healthcare."},
            {"id": "3", "name": "Admissions", "content": "Admissions to JKKN are based on merit and entrance examinations. The process typically starts in May each year."},
        ]

    def load_web_sources(self):
        for url in self.web_sources:
            content = scrape_webpage(url)
            self.documents.append({
                "id": url,
                "name": f"Web: {url}",
                "content": content
            })
        # Update document embeddings
        self.document_retrieval = OptimizedDocumentRetrieval(self.documents)

    async def process_user_input_async(self, user_input):
        try:
            cache_key = f"query_{hash(user_input)}"
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                return cached_response

            similar_docs, scores = self.document_retrieval.get_similar_documents(user_input)
            context = "\n".join([doc['content'] for doc in similar_docs])
            response = self.response_generator.generate_response(user_input, context)

            self.cache.set(cache_key, response)
            return response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Please try again later."

    def get_indexed_document_names(self):
        return [doc['name'] for doc in self.documents]