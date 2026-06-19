import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
import uuid
import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedding_model = None

def get_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = load_embedding_model()
    return embedding_model

chroma_client = chromadb.Client()

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def chunk_multiple_sources(sources, chunk_size=200, overlap=20):
    """
    sources: list of dicts [{"filename": ..., "text": ...}, ...]
    Returns: list of dicts [{"chunk": ..., "source": ...}, ...]
    """
    all_chunks = []
    for source in sources:
        chunks = chunk_text(source["text"], chunk_size=chunk_size, overlap=overlap)
        for chunk in chunks:
            all_chunks.append({"chunk": chunk, "source": source["filename"]})
    return all_chunks

def store_in_chromadb(chunks):
    """Store plain text chunks (no source tracking) — used for single text/YouTube input"""
    global chroma_client
    collection = chroma_client.get_or_create_collection(name="flashcards")
    embeddings = get_model().encode(chunks).tolist()
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{"source": "text"}],
            ids=[str(uuid.uuid4())]
        )
    print(f"Stored {len(chunks)} chunks in ChromaDB")

def store_tagged_chunks(tagged_chunks):
    """
    Store chunks that carry source metadata (used for multi-PDF input).
    tagged_chunks: list of dicts [{"chunk": ..., "source": ...}, ...]
    """
    global chroma_client
    collection = chroma_client.get_or_create_collection(name="flashcards")
    texts = [tc["chunk"] for tc in tagged_chunks]
    embeddings = get_model().encode(texts).tolist()
    for tc, embedding in zip(tagged_chunks, embeddings):
        collection.add(
            documents=[tc["chunk"]],
            embeddings=[embedding],
            metadatas=[{"source": tc["source"]}],
            ids=[str(uuid.uuid4())]
        )
    print(f"Stored {len(tagged_chunks)} tagged chunks in ChromaDB")

def retrieve_relevant_chunks(query, n_results=3):
    """Find most relevant chunks for a given query — returns plain text list"""
    global chroma_client
    collection = chroma_client.get_or_create_collection(name="flashcards")
    query_embedding = get_model().encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results['documents'][0]

def retrieve_relevant_chunks_with_sources(query, n_results=3):
    """Find most relevant chunks AND their source filenames"""
    global chroma_client
    collection = chroma_client.get_or_create_collection(name="flashcards")
    query_embedding = get_model().encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    return [{"chunk": doc, "source": meta.get("source", "unknown")} for doc, meta in zip(docs, metas)]