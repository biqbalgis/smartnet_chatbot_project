import faiss
import numpy as np
from embeddings.mistral_embed import get_mistral_embedding

# Load FAISS index
index = faiss.read_index('data/vectorstore/faq_index.faiss')

# Load documents
with open('data/vectorstore/docs.txt', 'r', encoding='utf-8') as f:
    documents = f.read().split('\n\n---\n\n')

def retrieve_faq_context(query, k=3):
    vec = np.array([get_mistral_embedding(query)], dtype='float32')
    if vec.shape[1] != index.d:
        raise ValueError(f"[❌] Embedding dimension mismatch: got {vec.shape[1]}, expected {index.d}")
    
    D, I = index.search(vec, k)
    return [documents[i] for i in I[0]]
