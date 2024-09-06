from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def create_embeddings(self, documents):
        """Create embeddings for a list of documents."""
        return [self.model.encode(doc) for doc in documents]

    def create_faiss_index(self, embeddings):
        """Create a FAISS index for similarity search."""
        embeddings = np.array(embeddings, dtype=np.float32)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index

    def search_similar(self, query, index, embeddings):
        """Search for similar documents based on the query."""
        query_embedding = np.array(self.model.encode([query]), dtype=np.float32)
        _, indices = index.search(query_embedding, k=5)
        return indices[0]
