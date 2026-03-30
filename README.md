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

### Clonar
```bash
git clone <seu-repositorio>
cd <projeto>
```

### VirtualEnv para Python3
1. **Criar e ativar um ambiente virtual antes de instalar dependências: (`.venv`):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. **Instalar as dependências:**
 ```bash
   pip install -r requirements.txt
   ```

3. **Configurar as variáveis de ambiente:**
    - Duplique o arquivo `.env.example` e renomeie para `.env`
    - Abra o arquivo `.env` e substitua os valores pelas suas chaves de API reais obtidas conforme instruções abaixo

    ```
    # Banco de dados
    DATABASE_URL=postgresql://postgres:postgres@localhost:5433/testedb

    # PDF
    PDF_PATH=document.pdf

    # Configurações do vetor
    PG_VECTOR_COLLECTION_NAME=pdf_documents
    LOCAL_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
    K=10
    ```

## Execução do projeto
Seguir a ordem de execução abaixo:

### 1. Executar a ingestão

```bash
  python3 src/ingest.py
```

### 2. Executar o chat determinístico

```bash
  python3 src/chat.py
```

---

### Entregável
1. Repositório público no GitHub contendo todo o código-fonte e README com instruções claras de execução do projeto.

---

---

## Testes
Executar todos os testes
```bash
python3 -m pytest -q
```
#### O que os testes integrados verificam
Os testes integrados localizados em tests/test_integrated_chat.py validam:
1. Extração determinística de ano
2. Extração determinística de faturamento
3. Listagem correta de empresas por ano
4. Normalização robusta de acentos
5. Busca híbrida literal + vetorial funcionando com DB real
6. Rejeição determinística de perguntas fora do contexto

Todas essas perguntas fora do contexto retornam sempre:
```
Não tenho informações necessárias para responder sua pergunta.
```

---

### Tecnologias obrigatórias
- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector
- Execução do banco de dados: Docker & Docker Compose (docker-compose fornecido no repositório de exemplo)

---

### Pacotes recomendados
- Split: from langchain_text_splitters import RecursiveCharacterTextSplitter
- Embeddings (OpenAI): from langchain_openai import OpenAIEmbeddings
- Embeddings (Gemini): from langchain_google_genai import GoogleGenerativeAIEmbeddings
- PDF: from langchain_community.document_loaders import PyPDFLoader
- Ingestão: from langchain_postgres import PGVector
- Busca: similarity_search_with_score(query, k=10)

---