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


def build_rag_chain():
    """Return a LangChain runnable that accepts a question string
    and returns an answer string, plus a retriever for source docs."""

    retriever = get_retriever()

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
    )

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
