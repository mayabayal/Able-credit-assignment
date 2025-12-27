
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class RAGSystem:
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2'):
        print(f"Loading embedding model: {embedding_model_name}")
        self.encoder = SentenceTransformer(embedding_model_name)
        # Using a flat L2 index for exact search as we expect < 100k chunks for a single file usually.
        # Dimension 384 is for all-MiniLM-L6-v2
        self.dimension = 384 
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = [] # Metadata storage corresponding to index

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """
        Embeds chunks and adds them to the FAISS index.
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Convert to float32 for FAISS
        embeddings_np = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings_np)
        self.documents.extend(chunks)
        print(f"Added {len(chunks)} documents to FAISS index. Total: {self.index.ntotal}")

    def query(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for the k most relevant chunks for the given query.
        """
        query_embedding = self.encoder.encode([query_text])
        query_embedding_np = np.array(query_embedding).astype('float32')
        
        distances, indices = self.index.search(query_embedding_np, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": float(distances[0][i])
                })
        
        return results

    def clear(self):
        """Resets the index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
