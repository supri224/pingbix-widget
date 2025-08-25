from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
from openai import OpenAI

# -------------------------
# Load and preprocess PDF
# -------------------------
reader = PdfReader(r"C:\Users\apple\Desktop\pingbix\pdf Pingbix.pdf")
pdf_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def chunk_text(text, chunk_size=500, overlap=50):
    chunks, start = [], 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

chunks = chunk_text(pdf_text, chunk_size=500, overlap=50)

# -------------------------
# Embeddings + Vector Index
# -------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
X = np.asarray(embeddings, dtype=np.float32)
nn = NearestNeighbors(metric="cosine")
nn.fit(X)

def search(query: str, top_k: int = 3):
    q_emb = model.encode([query], convert_to_numpy=True).astype(np.float32)
    if q_emb.ndim == 1:
        q_emb = q_emb.reshape(1, -1)
    k = min(top_k, X.shape[0])
    distances, indices = nn.kneighbors(q_emb, n_neighbors=k, return_distance=True)
    results = []
    for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
        similarity = 1.0 - float(dist)
        similarity = max(min(similarity, 1.0), -1.0)
        results.append({"rank": rank, "similarity": similarity, "chunk_index": int(idx), "text": chunks[int(idx)]})
    return results

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI(api_key="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")  # Replace with your key

# -------------------------
# FastAPI App + CORS
# -------------------------
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# API Model
# -------------------------
class Query(BaseModel):
    question: str

# -------------------------
# /chat Endpoint
# -------------------------
@app.post("/chat")
def chat(query: Query):
    hits = search(query.question, top_k=3)
    context = "\n".join(r["text"] for r in hits)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer only using Pingbix company documents."},
            {"role": "user", "content": f"Question: {query.question}\n\nContext:\n{context}"}
        ]
    )
    return {"answer": response.choices[0].message.content}

# -------------------------
# Serve static files (frontend)
# -------------------------
app.mount("/", StaticFiles(directory=".", html=True), name="static")
