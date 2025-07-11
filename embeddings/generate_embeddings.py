import re
import os
import faiss
import numpy as np
from dotenv import load_dotenv
load_dotenv()

from embeddings.mistral_embed import get_mistral_embedding

# Load and preprocess the FAQ document
with open('data/faq_document.md', 'r', encoding='utf-8') as f:
    content = f.read()

faq_sections = re.split(r'\n\* (?=[A-Z ]+:)', content)
faq_sections = [sec.strip() for sec in faq_sections if sec.strip()]

# Generate embeddings using Mistral API
embeddings = [get_mistral_embedding(text) for text in faq_sections]
embeddings_array = np.vstack(embeddings).astype("float32")


# Create FAISS index
index = faiss.IndexFlatL2(embeddings_array.shape[1])
index.add(embeddings_array)



# Save FAISS index and original docs
os.makedirs("data/vectorstore", exist_ok=True)
faiss.write_index(index, 'data/vectorstore/faq_index.faiss')

with open('data/vectorstore/docs.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(faq_sections))

print(" Embeddings generated and FAISS index saved.")
