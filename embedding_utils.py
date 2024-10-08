from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from config import EMBEDDING_MODEL

class EmbeddingUtil:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.doc_ids = []
        self.embeddings = None

    def create_embeddings(self, texts):
        return self.model.encode(texts, show_progress_bar=False)

    def create_faiss_index(self, embeddings, doc_ids):
        self.doc_ids = doc_ids
        self.embeddings = embeddings
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype('float32'))

    def search_similar(self, query, k=5):
        if self.index is None or len(self.doc_ids) == 0:
            return [], []
        query_vector = self.create_embeddings([query])[0]
        D, I = self.index.search(np.array([query_vector]).astype('float32'), k)
        return [self.doc_ids[i] for i in I[0] if i < len(self.doc_ids)], D[0].tolist()

    def update_index(self, new_texts, new_doc_ids):
        new_embeddings = self.create_embeddings(new_texts)
        if self.embeddings is None:
            self.create_faiss_index(new_embeddings, new_doc_ids)
        else:
            self.embeddings = np.vstack((self.embeddings, new_embeddings))
            self.doc_ids.extend(new_doc_ids)
            if self.index is None:
                self.create_faiss_index(self.embeddings, self.doc_ids)
            else:
                self.index.add(new_embeddings.astype('float32'))