import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedding_model = load_embedding_model()

# ── In-memory vector store (replaces ChromaDB) ──
_store = {
    "chunks": [],       # list of text chunks
    "embeddings": None, # numpy array of embeddings
    "sources": []        # list of source filenames (for multi-PDF)
}


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def store_in_chromadb(chunks):
    """Stores chunks + embeddings in memory (function name kept for compatibility)"""
    global _store
    embeddings = embedding_model.encode(chunks)
    _store["chunks"] = chunks
    _store["embeddings"] = np.array(embeddings)
    _store["sources"] = ["text"] * len(chunks)
    print(f"Stored {len(chunks)} chunks in memory")


def retrieve_relevant_chunks(query, n_results=3):
    """Cosine similarity search over in-memory store"""
    global _store
    if _store["embeddings"] is None or len(_store["chunks"]) == 0:
        return []

    query_embedding = embedding_model.encode([query])[0]
    chunk_embeddings = _store["embeddings"]

    # Cosine similarity
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
    chunk_norms = chunk_embeddings / (np.linalg.norm(chunk_embeddings, axis=1, keepdims=True) + 1e-10)
    similarities = chunk_norms @ query_norm

    top_indices = np.argsort(similarities)[::-1][:n_results]
    return [_store["chunks"][i] for i in top_indices]


# ── Multi-source (multi-PDF) support ──

def chunk_multiple_sources(sources, chunk_size=500, overlap=50):
    """
    sources: list of dicts [{"text": ..., "filename": ...}, ...]
    Returns list of dicts [{"chunk": ..., "source": ...}, ...]
    """
    tagged_chunks = []
    for src in sources:
        chunks = chunk_text(src["text"], chunk_size, overlap)
        for chunk in chunks:
            tagged_chunks.append({"chunk": chunk, "source": src["filename"]})
    return tagged_chunks


def store_tagged_chunks(tagged_chunks):
    global _store
    texts = [item["chunk"] for item in tagged_chunks]
    sources = [item["source"] for item in tagged_chunks]
    embeddings = embedding_model.encode(texts)
    _store["chunks"] = texts
    _store["embeddings"] = np.array(embeddings)
    _store["sources"] = sources
    print(f"Stored {len(texts)} tagged chunks in memory")


def retrieve_relevant_chunks_with_sources(query, n_results=3):
    global _store
    if _store["embeddings"] is None or len(_store["chunks"]) == 0:
        return []

    query_embedding = embedding_model.encode([query])[0]
    chunk_embeddings = _store["embeddings"]

    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
    chunk_norms = chunk_embeddings / (np.linalg.norm(chunk_embeddings, axis=1, keepdims=True) + 1e-10)
    similarities = chunk_norms @ query_norm

    top_indices = np.argsort(similarities)[::-1][:n_results]
    return [
        {"chunk": _store["chunks"][i], "source": _store["sources"][i]}
        for i in top_indices
    ]