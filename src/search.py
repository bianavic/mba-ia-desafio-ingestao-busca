import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres import PGVector

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


def search_prompt(question):
    vectorstore = get_vectorstore()
    top_k = int(os.getenv("RETRIEVAL_TOP_K", "10"))
    results = vectorstore.similarity_search_with_score(question, k=top_k)

    if not results:
        return NO_CONTEXT_ANSWER

    contexto = "\n\n".join(doc.page_content for doc, _score in results)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)

    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content
