"""
Offline ingestion pipeline: load knowledge-base documents, chunk them,
embed with OpenAI text-embedding-3-small, and persist to ChromaDB.

Usage:
    python ingest.py                      # uses OPENAI_API_KEY from env / .env
    OPENAI_API_KEY=sk-xxx python ingest.py
"""

import os
import glob
import hashlib

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import config

load_dotenv()


def _file_id(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()[:12]


def load_documents(data_dir: str) -> list[dict]:
    """Read every .md / .txt file in *data_dir* and return a list of dicts
    with keys 'text', 'source', and 'title'."""
    docs = []
    for pattern in ("*.md", "*.txt"):
        for fpath in sorted(glob.glob(os.path.join(data_dir, pattern))):
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
            title = os.path.splitext(os.path.basename(fpath))[0].replace("_", " ").title()
            docs.append({"text": text, "source": fpath, "title": title})
    return docs


def chunk_documents(docs: list[dict]) -> list:
    """Split documents into overlapping chunks using LangChain splitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n---", "\n\n", "\n", " "],
    )

    all_chunks = []
    for doc in docs:
        chunks = splitter.create_documents(
            texts=[doc["text"]],
            metadatas=[{"source": doc["source"], "title": doc["title"]}],
        )
        all_chunks.extend(chunks)

    return all_chunks


def build_vectorstore(chunks: list, persist_dir: str) -> Chroma:
    """Embed all chunks and store in ChromaDB."""
    import shutil

    embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        print(f"  Cleared old vector store at {persist_dir}")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=config.COLLECTION_NAME,
    )
    return vectorstore


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Set OPENAI_API_KEY environment variable or add it to .env")
        raise SystemExit(1)

    print(f"[1/3] Loading documents from {config.DATA_DIR} ...")
    docs = load_documents(config.DATA_DIR)
    print(f"       Found {len(docs)} documents.")

    print("[2/3] Chunking documents ...")
    chunks = chunk_documents(docs)
    print(f"       Created {len(chunks)} chunks (size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP}).")

    print(f"[3/3] Embedding & storing in ChromaDB at {config.CHROMA_PERSIST_DIR} ...")
    vs = build_vectorstore(chunks, config.CHROMA_PERSIST_DIR)
    print(f"       Done. Collection '{config.COLLECTION_NAME}' has {vs._collection.count()} vectors.")


if __name__ == "__main__":
    main()
