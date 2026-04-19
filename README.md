# RoboRAG — Retrieval-Augmented Generation for Robotics Q&A

A RAG-powered web application that answers robotics and motion planning questions using OpenAI GPT-4o-mini, grounded in a curated knowledge base of robotics documentation.

**Course:** DS552 — Generative AI, Worcester Polytechnic Institute  
**Author:** Piyush Thapar

## Features

- Natural-language Q&A for robotics, motion planning, MoveIt 2, ROS 2
- Retrieval-Augmented Generation — answers are grounded in source documents
- Source citations shown alongside every answer
- Clean chat interface built with Streamlit
- 153% improvement in ROUGE-1 over standalone LLM (verified on 20 benchmark questions)

## Architecture

```
User Question
     │
     ▼
┌─────────────┐     ┌───────────────────┐
│  Streamlit   │────▶│ OpenAI Embeddings  │
│   Web UI     │     │ text-embedding-3   │
└─────┬───────┘     └────────┬──────────┘
      │                      │
      │                      ▼
      │              ┌──────────────┐
      │              │   ChromaDB    │
      │              │ Vector Store  │
      │              └──────┬───────┘
      │                     │ top-5 chunks
      │                     ▼
      │              ┌──────────────┐
      └─────────────▶│   OpenAI      │
                     │  GPT-4o-mini  │
                     └──────┬───────┘
                            │
                            ▼
                    Grounded Answer
                   + Source Citations
```

## Quick Start (Local)

### 1. Prerequisites

- Python 3.10+
- An OpenAI API key: https://platform.openai.com/api-keys

### 2. Clone and install

```bash
cd Module_7/RoboRAG
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Set your API key

Create a `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Ingest the knowledge base

```bash
python ingest.py
```

This chunks the documents in `data/knowledge_base/`, embeds them with OpenAI's `text-embedding-3-small`, and stores the vectors in `chroma_db/`.

### 5. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 6. Run evaluation (optional)

```bash
python evaluate.py
```

Results are saved to `eval/results/eval_results.json`.

## Deploying to Streamlit Cloud

1. Push this project to a **public GitHub repository**.

2. Go to https://share.streamlit.io/ and sign in with GitHub.

3. Click **New app** → select your repo → set the main file to `app.py`.

4. Under **Advanced settings**, add your secret:
   ```
   OPENAI_API_KEY = "sk-your-key-here"
   ```

5. Click **Deploy**. The app will be live at `https://your-app.streamlit.app`.

> **Important:** Run `python ingest.py` locally first and commit the `chroma_db/` folder to your repo so the deployed app can load the pre-built vector store.

## Project Structure

```
RoboRAG/
├── app.py                  # Streamlit web application
├── config.py               # Central configuration
├── ingest.py               # Document ingestion pipeline
├── rag_chain.py            # RAG pipeline (retrieval + GPT-4o-mini)
├── evaluate.py             # Evaluation script (ROUGE, F1, P@K)
├── requirements.txt        # Python dependencies
├── .env                    # API key (not committed)
├── .gitignore
├── .streamlit/
│   └── config.toml         # Streamlit theme
├── data/
│   └── knowledge_base/     # Curated robotics documents
├── chroma_db/              # Persisted vector store (after ingestion)
├── eval/
│   ├── qa_pairs.json       # Benchmark Q&A pairs (20 questions)
│   └── results/            # Evaluation output
└── report/
    └── report.md           # Project report
```

## Technology Stack

| Component      | Technology                        |
|---------------|-----------------------------------|
| LLM           | OpenAI GPT-4o-mini                |
| Embeddings    | OpenAI text-embedding-3-small     |
| Vector DB     | ChromaDB (local, persisted)       |
| Orchestration | LangChain                         |
| Frontend      | Streamlit                         |
| Evaluation    | rouge-score, scikit-learn, psutil |
| Language      | Python 3.10+                      |
