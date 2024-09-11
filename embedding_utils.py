from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def create_embeddings(self, texts):
        return self.model.encode(texts)

    def compute_similarity(self, embedding1, embedding2):
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))