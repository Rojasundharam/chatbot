from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.doc_ids = []

    def create_embeddings(self, texts):
        return self.model.encode(texts)

    def create_faiss_index(self, embeddings, doc_ids):
        self.doc_ids = doc_ids
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype('float32'))

    def search_similar(self, query, k=5):
        query_vector = self.create_embeddings([query])[0]
        D, I = self.index.search(np.array([query_vector]).astype('float32'), k)
        return [self.doc_ids[i] for i in I[0]]