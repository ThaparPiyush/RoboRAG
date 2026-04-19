"""
RAG chain: retrieve relevant chunks from ChromaDB, build a prompt,
and call OpenAI GPT-4o-mini to generate a grounded answer.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import config

load_dotenv()


def get_llm():
    return ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
    )


def get_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
    return Chroma(
        persist_directory=config.CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name=config.COLLECTION_NAME,
    )


def get_retriever(top_k: int = config.TOP_K):
    vs = get_vectorstore()
    return vs.as_retriever(search_type="similarity", search_kwargs={"k": top_k})


def format_docs(docs) -> str:
    formatted = []
    for i, doc in enumerate(docs, 1):
        title = doc.metadata.get("title", "Unknown")
        formatted.append(f"[Source {i}: {title}]\n{doc.page_content}")
    return "\n\n".join(formatted)


# ── New: retrieval with similarity scores (for confidence indicator) ─────────

def retrieve_with_scores(vs, query: str, top_k: int = config.TOP_K):
    """Return (docs, relevance_scores) where scores are 0-1 (higher = better)."""
    results = vs.similarity_search_with_relevance_scores(query, k=top_k)
    docs = [doc for doc, _ in results]
    scores = [max(0.0, score) for _, score in results]
    return docs, scores


# ── New: RAG query with multi-turn memory ────────────────────────────────────

def answer_question(llm, vs, question: str, chat_history: str = ""):
    """Full RAG query with confidence scores and conversation memory.
    Returns (answer, docs, scores)."""
    docs, scores = retrieve_with_scores(vs, question)
    context = format_docs(docs)

    prompt = ChatPromptTemplate.from_template(config.RAG_PROMPT_TEMPLATE_V2)
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "system_prompt": config.SYSTEM_PROMPT,
        "context": context,
        "question": question,
        "chat_history": chat_history,
    })
    return answer, docs, scores


# ── New: follow-up question generation ───────────────────────────────────────

def generate_followups(llm, vs, question: str, answer: str) -> list[str]:
    """Generate follow-up questions, validated against the KB.
    Only returns questions that the knowledge base can actually answer."""
    prompt = ChatPromptTemplate.from_template(config.FOLLOWUP_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question, "answer": answer})

    candidates = []
    for line in result.strip().split("\n"):
        cleaned = line.strip().lstrip("0123456789.-) ").strip()
        if cleaned and len(cleaned) > 10:
            candidates.append(cleaned)

    # Blocklist: phrases that ask about things outside the KB
    _blocklist = [
        "compare to other", "compared to other", "traditional",
        "alternative", "vs other", "outside of", "beyond",
        "real-world example", "industry", "production",
        "implement", "configure", "install", "set up", "setup",
        "code example", "tutorial", "step by step",
    ]

    def _is_safe(q: str) -> bool:
        q_lower = q.lower()
        return not any(phrase in q_lower for phrase in _blocklist)

    # Validate: blocklist + retrieval confidence check
    validated = []
    for fq in candidates[:6]:
        if not _is_safe(fq):
            continue
        _, scores = retrieve_with_scores(vs, fq, top_k=3)
        top_score = max(scores) if scores else 0
        if top_score >= 0.42:
            validated.append(fq)
        if len(validated) == 3:
            break

    return validated


# ── Legacy: original chain for evaluate.py backward compatibility ────────────

def build_rag_chain():
    """Return a LangChain runnable that accepts a question string
    and returns an answer string, plus a retriever for source docs."""

    retriever = get_retriever()
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(config.RAG_PROMPT_TEMPLATE)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "system_prompt": lambda _: config.SYSTEM_PROMPT,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def query(question: str) -> dict:
    """High-level helper: run the full RAG pipeline and return
    answer + source documents."""
    chain, retriever = build_rag_chain()
    source_docs = retriever.invoke(question)
    answer = chain.invoke(question)
    return {"answer": answer, "source_documents": source_docs}


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What motion planner should I use for a 7-DOF arm?"
    print(f"Question: {q}\n")
    result = query(q)
    print(f"Answer:\n{result['answer']}\n")
    print("Sources:")
    for doc in result["source_documents"]:
        print(f"  - {doc.metadata.get('title', '?')}")
