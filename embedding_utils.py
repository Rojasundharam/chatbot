from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tfidf_vectorizer = TfidfVectorizer()

    def create_embeddings(self, documents):
        """Create embeddings for a list of documents."""
        embeddings = self.model.encode(documents, show_progress_bar=True)
        return embeddings

    def create_tfidf_matrix(self, documents):
        """Create TF-IDF matrix for a list of documents."""
        return self.tfidf_vectorizer.fit_transform(documents)

    def create_faiss_index(self, embeddings):
        """Create a FAISS index for similarity search."""
        embeddings = np.array(embeddings).astype('float32')
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index

    def search_similar(self, query, index, embeddings, k=5):
        """Search for similar documents based on the query."""
        query_embedding = self.model.encode([query]).astype('float32')
        _, indices = index.search(query_embedding, k)
        return indices[0]

    def hybrid_search(self, query, index, embeddings, tfidf_matrix, k=10):
        """Perform a hybrid search using both embeddings and TF-IDF."""
        embedding_indices = self.search_similar(query, index, embeddings, k)        
        
        tfidf_query_vec = self.tfidf_vectorizer.transform([query])
        tfidf_similarities = tfidf_query_vec.dot(tfidf_matrix.T).toarray()[0]
        tfidf_indices = tfidf_similarities.argsort()[-k:][::-1]
        
        combined_indices = list(set(embedding_indices) | set(tfidf_indices))        
        
        return combined_indices[:k]