import os
import re

from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import create_engine, text

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

NO_CONTEXT_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

_STOP_WORDS = {
    "qual", "quais", "como", "quando", "onde", "que", "por", "para", "com",
    "sem", "uma", "uns", "dos", "das", "nos", "nas", "foi", "foram", "ser",
    "ter", "sua", "seu", "empresa", "empresas", "faturamento", "fundação",
    "fundadas", "fundada", "fundado", "ano", "the", "and",
}


def get_vectorstore():
    embeddings = OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large"),
    )
    return PGVector(
        connection=os.getenv("DATABASE_URL"),
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION_NAME", "pdf_documents"),
    )


def get_llm():
    return ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3:latest"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
    )


def _extract_keywords(question):
    """Extract meaningful keywords for literal DB search."""
    words = re.findall(r"\b\w+\b", question)
    keywords = [w for w in words if len(w) > 2 and w.lower() not in _STOP_WORDS]
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", question)
    return list(dict.fromkeys(keywords + years))


def _keyword_search(question):
    """Search chunks by keyword matching (literal/hybrid search).

    Tries ALL keywords combined (AND) first for precision.
    Falls back to individual keywords if no combined match.
    """
    database_url = os.getenv("DATABASE_URL")
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Try all keywords combined (AND) for precise matches
        conditions = " AND ".join(
            f"document ILIKE :kw{i}" for i in range(len(keywords))
        )
        params = {f"kw{i}": f"%{kw}%" for i, kw in enumerate(keywords)}
        rows = conn.execute(
            text(f"SELECT document FROM langchain_pg_embedding WHERE {conditions}"),
            params,
        ).fetchall()

        if rows:
            return [content for (content,) in rows]

        # Fallback: individual keywords
        seen = set()
        docs = []
        for kw in keywords:
            rows = conn.execute(
                text(
                    "SELECT document FROM langchain_pg_embedding "
                    "WHERE document ILIKE :pattern LIMIT 5"
                ),
                {"pattern": f"%{kw}%"},
            ).fetchall()
            for (content,) in rows:
                if content not in seen:
                    seen.add(content)
                    docs.append(content)
        return docs


def _filter_lines(chunks, keywords):
    """Keep only lines containing at least one keyword, plus the header."""
    filtered = []
    header = "Nome da empresa | Faturamento | Ano de fundação"
    for chunk in chunks:
        lines = chunk.strip().split("\n")
        relevant = [header]
        for line in lines:
            if line.strip() == header or "|" in line:
                continue
            if any(kw.lower() in line.lower() for kw in keywords):
                relevant.append(line)
        if len(relevant) > 1:
            filtered.append("\n".join(relevant))
    return filtered


def search_prompt(question):
    vectorstore = get_vectorstore()
    top_k = int(os.getenv("RETRIEVAL_TOP_K", "10"))

    # Hybrid: keyword (literal) first, vector (semantic) as fallback
    keywords = _extract_keywords(question)
    keyword_docs = _keyword_search(question)

    if keyword_docs:
        all_contents = _filter_lines(keyword_docs[:top_k], keywords)
    else:
        vector_results = vectorstore.similarity_search_with_score(question, k=top_k)
        all_contents = [doc.page_content for doc, _score in vector_results]

    if not all_contents:
        return NO_CONTEXT_ANSWER

    contexto = "\n\n".join(all_contents)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)

    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content