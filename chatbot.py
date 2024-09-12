import asyncio
import time
import numpy as np
import faiss
import torch
import nltk
from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer
from transformers import BertTokenizer, BertModel, GPT2LMHeadModel, GPT2Tokenizer
from cachetools import TTLCache, cached
import functools
import httpx
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_nltk_data():
    resources = [
        'punkt',
        'averaged_perceptron_tagger',
        'wordnet'
    ]
    
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
            logging.info(f"NLTK resource '{resource}' is already downloaded.")
        except LookupError:
            logging.info(f"Downloading NLTK resource: {resource}")
            nltk.download(resource, quiet=True)
            logging.info(f"Successfully downloaded NLTK resource: {resource}")

# Download required NLTK data
download_nltk_data()

class OptimizedDocumentRetrieval:
    def __init__(self, documents):
        self.documents = documents
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.build_index()

    def build_index(self):
        embeddings = self.model.encode([doc['content'] for doc in self.documents])
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def get_similar_documents(self, query, k=5):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        similar_docs = [self.documents[i] for i in indices[0]]
        scores = [1 / (1 + d) for d in distances[0]]  # Convert distances to similarity scores
        return similar_docs, scores

class EnhancedQueryRewriter:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.eval()

    def get_bert_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].numpy()[0]

    def rewrite_query(self, query):
        try:
            original_embedding = self.get_bert_embedding(query)
            
            tokens = nltk.word_tokenize(query.lower())
            pos_tags = nltk.pos_tag(tokens)
            
            expanded_tokens = []
            for token, pos in pos_tags:
                expanded_tokens.append(token)
                if pos.startswith('N') or pos.startswith('V'):
                    synsets = wordnet.synsets(token)
                    for synset in synsets[:2]:
                        for lemma in synset.lemmas():
                            if lemma.name() != token:
                                expanded_tokens.append(lemma.name())
            
            expanded_query = ' '.join(expanded_tokens)
            expanded_embedding = self.get_bert_embedding(expanded_query)
            
            combined_embedding = (original_embedding + expanded_embedding) / 2
            
            return expanded_query, combined_embedding
        except Exception as e:
            logging.error(f"Error in query rewriting: {str(e)}")
            return query, self.get_bert_embedding(query)  # Return original query and embedding on error

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
        self.query_rewriter = EnhancedQueryRewriter()
        self.response_generator = ImprovedResponseGenerator()
        self.cache = TTLCache(maxsize=100, ttl=3600)  # Cache with max 100 items, expiring after 1 hour
        self.http_client = httpx.AsyncClient()
        self.last_update_time = time.time()

    def load_documents(self):
        # This is a placeholder implementation. In a real scenario, you'd load your actual documents here.
        return [
            {"id": "1", "name": "JKKN Overview", "content": "JKKN Educational Institutions offer a wide range of programs including engineering, management, and health sciences. Founded in 1995, JKKN has become a leading educational group in the region."},
            {"id": "2", "name": "Admission Process", "content": "To apply for admission to JKKN, students need to follow these steps: 1) Fill out the online application form, 2) Submit required documents, 3) Pay the application fee, 4) Attend the entrance exam if required for the chosen program."},
            {"id": "3", "name": "Campus Facilities", "content": "JKKN campuses are equipped with state-of-the-art facilities including modern laboratories, libraries with extensive collections, sports complexes, and comfortable student housing. Wi-Fi is available throughout the campus."},
            {"id": "4", "name": "Faculty", "content": "JKKN boasts a highly qualified faculty with many holding PhDs from renowned universities. Our professors are dedicated to providing quality education and are actively involved in research and industry collaborations."},
            {"id": "5", "name": "Placements", "content": "JKKN has an excellent track record in placements. Our dedicated placement cell works tirelessly to ensure students get opportunities in top companies. Many of our alumni are working in Fortune 500 companies."}
        ]

    @cached(cache=lambda self: self.cache)
    def get_similar_documents(self, query, k=5):
        return self.document_retrieval.get_similar_documents(query, k)

    @functools.lru_cache(maxsize=100)
    def query_rewrite(self, query):
        return self.query_rewriter.rewrite_query(query)

    async def fetch_external_data(self, url):
        # This is a placeholder. In a real scenario, you'd fetch actual external data.
        await asyncio.sleep(1)  # Simulate network delay
        return {"info": "JKKN is currently accepting applications for the upcoming academic year. Visit our website for more details."}

    async def process_user_input_async(self, user_input):
        try:
            rewritten_query, query_embedding = self.query_rewrite(user_input)
            similar_docs, scores = self.get_similar_documents(rewritten_query)
            
            external_data_task = asyncio.create_task(self.fetch_external_data("https://api.example.com/data"))
            
            context = "\n".join([doc['content'] for doc in similar_docs[:2]])
            response = self.response_generator.generate_response(rewritten_query, context)
            
            try:
                external_data = await external_data_task
                enhanced_response = f"{response}\n\nAdditional info: {external_data['info']}"
            except Exception as e:
                logging.error(f"Error fetching external data: {str(e)}")
                enhanced_response = response  # Fallback to original response if external data fetch fails
            
            return enhanced_response
        except Exception as e:
            logging.error(f"Error processing user input: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Please try again later."

    def get_indexed_document_names(self):
        return [doc['name'] for doc in self.documents]

    async def close(self):
        await self.http_client.aclose()