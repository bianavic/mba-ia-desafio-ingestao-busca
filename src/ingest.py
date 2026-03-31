import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def ingest_pdf():
    """Carrega PDF, divide em chunks, embeda e armazena no pgVector."""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Erro: DATABASE_URL não configurada.")
        sys.exit(1)

    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    if not os.path.exists(pdf_path):
        print(f"Erro: arquivo não encontrado: {pdf_path}")
        sys.exit(1)

    print(f"Carregando PDF: {pdf_path}")
    documents = PyPDFLoader(pdf_path).load()
    print(f"Páginas carregadas: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
    )
    chunks = splitter.split_documents(documents)
    print(f"Chunks gerados: {len(chunks)}")

    embeddings = OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large"),
    )

    vectorstore = PGVector(
        connection=database_url,
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION_NAME", "pdf_documents"),
    )

    vectorstore.add_documents(chunks)
    print(f"Ingestão concluída. {len(chunks)} chunks inseridos.")


def main():
    ingest_pdf()


if __name__ == "__main__":
    main()