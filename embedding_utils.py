from sentence_transformers import SentenceTransformer
import faiss

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def create_embeddings(self, documents):
        return [self.model.encode(doc) for doc in documents]

    def create_faiss_index(self, embeddings):
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index

    def search_similar(self, query, index, embeddings):
        query_embedding = self.model.encode([query])
        _, indices = index.search(query_embedding, k=5)
        return indices[0]
