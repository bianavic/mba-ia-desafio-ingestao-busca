# Desafio MBA Engenharia de Software com IA - Full Cycle

## Índice
1. [**Objetivo**](#objetivo)
2. [**Tecnologias obrigatórias**](#tecnologias-obrigatórias)
3. [**Pacotes recomendados**](#pacotes-recomendados)
4. [**Requisitos**](#requisitos)
5. [**Estrutura obrigatória do projeto**](#estrutura-obrigatória-do-projeto)
6. [**Repositórios úteis**](#repositórios-úteis)
7. [**Configuração do Ambiente**](#configuração-do-ambiente)
8. [**Execução**](#execução-do-projeto)
9. [**Testes**](#testes)

## Objetivo

Você deve entregar um software capaz de:
1. Ingestão: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
2. Busca: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

#### Exemplo no CLI
```text
Faça sua pergunta:

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

---

Perguntas fora do contexto:

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## Tecnologias obrigatórias
- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector
- Execução do banco de dados: Docker & Docker Compose (docker-compose fornecido no repositório de exemplo)

---

## Pacotes recomendados
- Split: from langchain_text_splitters import RecursiveCharacterTextSplitter
- Embeddings (OpenAI): from langchain_openai import OpenAIEmbeddings
- Embeddings (Gemini): from langchain_google_genai import GoogleGenerativeAIEmbeddings
- PDF: from langchain_community.document_loaders import PyPDFLoader
- Ingestão: from langchain_postgres import PGVector
- Busca: similarity_search_with_score(query, k=10)

---

### Ollama
- URL da API: http://localhost:11434
- Modelo de embeddings: mxbai-embed-large
- Modelo de LLM para responder: llama3:latest

---

## Requisitos
1. Ingestão do PDF
- O PDF deve ser dividido em chunks de 1000 caracteres com overlap de 150.
- Cada chunk deve ser convertido em embedding.
- Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.
2. Consulta via CLI
- Criar um script Python para simular um chat no terminal.
- Passos ao receber uma pergunta:
    - Vetorizar a pergunta.
    - Buscar os 10 resultados mais relevantes (k=10) no banco vetorial.
    - Montar o prompt e chamar a LLM.
    - Retornar a resposta ao usuário.
    - Prompt a ser utilizado:
```text
CONTEXTO:
{resultados concatenados do banco de dados}

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
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

---

## Estrutura obrigatória do projeto
Faça um fork do repositório para utilizar a estrutura abaixo: [Clique aqui](https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca/)
```
├── docker-compose.yml
├── requirements.txt      # Dependências
├── .env.example          # Template da variável OPENAI_API_KEY
├── src/
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Script de busca
│   ├── chat.py           # CLI para interação com usuário
├── document.pdf          # PDF para ingestão
└── README.md             # Instruções de execução
```

---

## Repositórios úteis:
[Curso de nivelamento com LangChain](https://github.com/devfullcycle/mba-ia-niv-introducao-langchain/)

[Template básico com estrutura do projeto](https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca/)

---

## Configuração do Ambiente

### Pré-requisitos
- Python 3.10+
- Docker & Docker Compose
- [Ollama](https://ollama.ai) instalado localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/bianavic/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

### 2. Criar ambiente virtual e instalar dependências
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Duplique `.env.example` para `.env` e preencha:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
LLM_TEMPERATURE=0.0
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/rag
PGVECTOR_COLLECTION_NAME=pdf_documents
PDF_PATH=document.pdf
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=10
```

### 4. Subir o banco de dados
```bash
docker compose up -d
```
Aguarde o PostgreSQL + pgVector ficar healthy (extensão `vector` é criada automaticamente).

### 5. Baixar modelos do Ollama
```bash
ollama pull llama3:latest
ollama pull mxbai-embed-large
```

---

## Execução do projeto

### 1. Ingestão do PDF
```bash
python3 src/ingest.py
```
Saída esperada: `Ingestão concluída. X chunks inseridos.`

### 2. Chat interativo
```bash
python3 src/chat.py
```
Digite sua pergunta e receba a resposta. Para sair: `exit`, `sair`, `quit` ou `Ctrl+C`.

---

## Testes

```bash
python3 -m pytest -q                                  # Todos os testes
python3 -m pytest tests/test_integrated_chat.py -q    # Testes integrados
python3 -m pytest -k "test_name" -q                   # Teste individual
```

> Os testes integrados requerem PostgreSQL e Ollama rodando localmente com dados já ingeridos.

#### O que os testes integrados verificam
1. Extração determinística de ano de fundação
2. Extração determinística de faturamento
3. Listagem correta de empresas por ano
4. Normalização robusta de acentos
5. Busca híbrida literal + vetorial com DB real
6. Rejeição determinística de perguntas fora do contexto

Perguntas fora do contexto retornam sempre:
```
Não tenho informações necessárias para responder sua pergunta.
```

---

### Entregável
Repositório público no GitHub contendo todo o código-fonte e README com instruções claras de execução do projeto.