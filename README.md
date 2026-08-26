# Enterprise AI Agent Platform

A full-stack AI agent platform for creating configurable AI assistants with multi-provider LLM support, persistent conversations, document-based knowledge bases, semantic search, and Retrieval-Augmented Generation (RAG).

The platform supports both local models through Ollama and cloud inference through Groq, while PostgreSQL + pgvector provides vector storage and semantic document retrieval.

---

## Features

### AI Agent Management

- Create, edit, and delete AI agents
- Configure model provider
- Select LLM model
- Configure temperature
- Define custom system prompts
- Attach a Knowledge Base to an agent

### Multi-Provider LLM Support

The platform uses a provider abstraction layer so agents can work with multiple LLM providers.

Currently supported:

- Ollama — local LLM inference
- Groq — cloud LLM inference

The architecture can be extended with additional providers.

### Streaming Chat

- Real-time streamed AI responses
- Persistent conversations
- Conversation history
- Multiple conversations per agent
- Markdown rendering
- Code block rendering

### Knowledge Bases

Users can create Knowledge Bases and upload documents containing domain-specific information.

Supported document workflow:

1. Upload document
2. Extract text
3. Split text into chunks
4. Generate embeddings
5. Store embeddings in PostgreSQL
6. Search relevant chunks using vector similarity
7. Add retrieved context to the LLM prompt

### Retrieval-Augmented Generation (RAG)

Agents can be connected to a Knowledge Base.

When a user asks a question:

```text
User Question
     |
     v
Agent
     |
     v
Knowledge Base
     |
     v
Query Embedding
     |
     v
pgvector Similarity Search
     |
     v
Relevant Document Chunks
     |
     v
RAG Context
     |
     v
Ollama / Groq
     |
     v
Grounded Response
```

This allows agents to answer questions using uploaded private/domain-specific documents rather than relying only on the model's general knowledge.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector
- FastEmbed

### Frontend

- React
- Vite
- JavaScript
- CSS
- React Markdown
- remark-gfm

### AI / LLM

- Ollama
- Groq
- Embedding-based semantic retrieval
- Retrieval-Augmented Generation (RAG)

---

## Architecture

```text
                       React + Vite
                            |
                            | REST / Streaming HTTP
                            v
                       FastAPI API
                            |
              +-------------+-------------+
              |                           |
              v                           v
         Agent Service              Knowledge Service
              |                           |
              v                           v
        Provider Layer              Document Processing
         /         \                       |
        /           \                      v
     Ollama         Groq               FastEmbed
                                         |
                                         v
                                   PostgreSQL
                                   + pgvector
                                         |
                                         v
                                  Semantic Search
                                         |
                                         v
                                     RAG Context
```

---

## Project Structure

```text
Enterprise-AI-Agent-Platform/
|
|-- backend/
|   |-- app/
|       |-- api/
|       |   |-- agents.py
|       |   |-- conversations.py
|       |   `-- knowledge_bases.py
|       |
|       |-- db/
|       |   `-- database.py
|       |
|       |-- models/
|       |
|       |-- providers/
|       |   |-- base.py
|       |   |-- registry.py
|       |   |-- ollama_provider.py
|       |   `-- groq_provider.py
|       |
|       |-- services/
|       |   |-- agent_service.py
|       |   |-- conversation_service.py
|       |   |-- document_processing_service.py
|       |   |-- embedding_service.py
|       |   |-- knowledge_base_service.py
|       |   |-- llm_service.py
|       |   `-- rag_service.py
|       |
|       `-- main.py
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- App.jsx
|   |   |-- App.css
|   |   `-- main.jsx
|   |
|   `-- package.json
|
|-- alembic/
|   `-- versions/
|
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- requirements.txt
`-- README.md
```

---

## Database

PostgreSQL is used for persistent application data.

The application stores:

- Agents
- Conversations
- Messages
- Knowledge Bases
- Knowledge Documents
- Knowledge Chunks
- Vector embeddings

Vector embeddings are stored using the PostgreSQL `pgvector` extension.

Database schema changes are managed using Alembic migrations.

---

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Enterprise-AI-Agent-Platform
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Configure the required values:

```env
DATABASE_URL=postgresql://postgres:your_password_here@localhost:5432/enterprise_ai

OPENAI_API_KEY=your_openai_api_key_here

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=your_ollama_model_here

GROQ_API_KEY=your_groq_api_key_here
```

Do not commit `.env`.

### 5. PostgreSQL + pgvector

Create the PostgreSQL database:

```text
enterprise_ai
```

The PostgreSQL installation must support the `vector` extension.

The project contains an Alembic migration that enables pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the backend

```bash
python -m uvicorn backend.app.main:app --reload
```

The API will run locally at:

```text
http://127.0.0.1:8000
```

### 8. Install frontend dependencies

Open another terminal:

```bash
cd frontend
npm install
```

### 9. Start the frontend

```bash
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

---

## Ollama Setup

Install and start Ollama before using local models.

Make sure the model configured for an agent is available locally.

Example:

```bash
ollama list
```

The application checks model availability before sending requests.

---

## Knowledge Base Workflow

Create a Knowledge Base from the web interface and upload a supported document.

The backend then:

```text
Document
   |
   v
Text Extraction
   |
   v
Chunking
   |
   v
FastEmbed
   |
   v
Vector Embeddings
   |
   v
PostgreSQL + pgvector
```

When an attached agent receives a question:

```text
Question
   |
   v
Embedding
   |
   v
Vector Similarity Search
   |
   v
Top Relevant Chunks
   |
   v
System Prompt Context
   |
   v
LLM
   |
   v
Grounded Answer
```

---

## RAG Example

An uploaded company security policy might contain:

```text
Employees must use multi-factor authentication for all company accounts.
```

A user can ask:

```text
How should employees keep their company accounts secure?
```

The system performs semantic retrieval, finds the relevant policy chunk, and provides it to the selected LLM as context.

This works even when the question does not exactly match the wording in the source document.

---

## API Overview

Key API areas include:

```text
/agents
/conversations
/knowledge-bases
/providers
```

Agent execution supports both standard and streaming responses.

```text
POST /agents/{agent_id}/run
POST /agents/{agent_id}/stream
```

Knowledge Bases support document upload and semantic retrieval.

---

## Security

Sensitive configuration is loaded through environment variables.

The following are excluded from Git:

- `.env`
- API keys
- Database credentials
- Python virtual environments
- `node_modules`
- Uploaded knowledge documents
- Temporary test files
- Local storage

Use `.env.example` as the configuration template.

---

## Screenshots

Screenshots of the application UI will be added here.

Suggested screenshots:

1. Agent dashboard
2. Agent configuration
3. Streaming conversation
4. Knowledge Base management
5. Document upload
6. RAG-powered response

---

## V1 Scope

Version 1 focuses on the core AI agent platform:

- Agent CRUD
- Multi-provider LLM architecture
- Ollama support
- Groq support
- Streaming responses
- Persistent conversation history
- Markdown/code rendering
- Knowledge Base management
- Document processing
- Embeddings
- pgvector semantic search
- Retrieval-Augmented Generation
- Agent-to-Knowledge-Base integration

---

## Future Improvements

Potential V2 features include:

- Authentication and user accounts
- Team workspaces
- Role-based access control
- Multiple Knowledge Bases per agent
- Agent tools/function calling
- Web search tools
- Usage analytics
- Token/cost tracking
- Background document processing
- Additional LLM providers
- Observability and tracing
- Docker deployment
- Automated testing and CI/CD

---

## Author

Built as a full-stack AI engineering project demonstrating:

- LLM application architecture
- Retrieval-Augmented Generation
- Vector databases
- Multi-provider AI integration
- FastAPI backend development
- React frontend development
- PostgreSQL database design
- Production-oriented configuration and deployment