# SargamAI

**Where content meets clarity.**

SargamAI is a production-grade Retrieval-Augmented Generation (RAG) application that transforms PDFs, YouTube videos, and CSV datasets into interactive, conversational knowledge bases. Built with **FastAPI** and **Next.js**, powered by state-of-the-art language models via OpenRouter, it features a modern terminal-inspired UI with PDF split-view, intelligent multi-modal querying, persistent chat history, and context-aware responses.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/next.js-16.1-black.svg)](https://nextjs.org/)
[![LangChain](https://img.shields.io/badge/langchain-1.2+-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Memory System](#-memory-system)
- [Data Schema](#-data-schema)
- [Security Considerations](#-security-considerations)

---

## ✨ Features

### Core Capabilities
- **Secure Authentication** - Firebase-backed user management with email/password authentication
- **PDF Processing** - Upload and automatically index PDF documents for semantic search with split-view display
- **YouTube Analysis** - Paste any YouTube URL to extract transcript, index it, and chat about the video
- **CSV Intelligence** - Upload CSV datasets and query them with natural language via a Pandas agent
- **Conversational RAG** - Ask natural language questions about your content with context-aware responses
- **Multi-Model Support** - Access GPT-4, Claude, Gemini, and Grok models through a unified interface
- **Persistent Chat History** - Conversations survive refreshes and are stored in Firestore
- **Auto-Load Intelligence** - Vectorstores load automatically when switching between documents
- **User Profiles** - Customizable display names and saved API keys per user

### UI/UX Features
- **Terminal-Inspired Thinking State** - Visual pipeline stages (PARSE → EMBED → SEARCH → RANK → GEN)
- **PDF Split-View** - Document viewer on left, chat interface on right for PDF files
- **Collapsible Source Chunks** - View retrieved document chunks with page numbers and excerpts
- **Modern Design System** - "Obsidian Ember" theme with custom Fontshare fonts (Satoshi, Clash Display, General Sans, JetBrains Mono)
- **Responsive & Fast** - Built with Next.js 16 + React 19 + Tailwind CSS v4

### Technical Highlights
- **FastAPI Backend** - Async REST API with JWT authentication
- **Next.js Frontend** - Server-side rendering, App Router, Turbopack
- **Multi-Modal Pipeline** - Unified RAG architecture handles PDFs, YouTube transcripts, and CSV datasets
- **Semantic Chunking** - Intelligent text splitting preserving context across 1000-character segments
- **Local Embeddings** - HuggingFace `all-MiniLM-L6-v2` runs locally (no API costs)
- **FAISS Vector Store** - High-performance similarity search with Firestore persistence (chunked <700KB)
- **Pandas Agent** - Natural language querying of structured data via LangChain agents
- **Conversational Memory** - Windowed memory tracks last 8 exchanges for context retention
- **Two-Stage Retrieval** - Condense-question chain + document QA chain for accurate responses
- **Cloud Ready** - Deploy backend on Render, frontend on Vercel

---

## 🏗 Architecture

OmniMind implements a modern, production-ready full-stack RAG architecture:

```
┌───────────────────────────────────────────────────────────────────┐
│                     NEXT.JS FRONTEND (CLIENT/)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ app/login    │  │ app/chat     │  │ app/profile  │             │
│  │ (Auth UI)    │  │ (Split-view) │  │ (Settings)   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  • NextJS                  • Tailwind CSS v4                      │
│  • Firebase Client SDK      • Terminal Aesthetic                  │
│  • PDF Split-View           • Source Chunks Display               │
└───────────────────────────────────────────────────────────────────┘
                            ↓ ↑ (REST API + JWT)
┌───────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (SERVER/)                      │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ routes/                                                   │    │
│  │  ├── auth.py       (Register endpoint)                    │    │
│  │  ├── upload.py     (PDF/YouTube/CSV ingestion)            │    │
│  │  ├── chat.py       (Message endpoint, returns sources)    │    │
│  │  ├── files.py      (List, delete, GET PDF bytes)          │    │
│  │  └── profile.py    (User settings, API key)               │    │
│  └───────────────────────────────────────────────────────────┘    │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ modules/                                                  │    │
│  │  ├── chains.py     (LCEL-based ConversationalRAGChain)    │    │
│  │  ├── rag.py        (Vectorstore creation, chunking)       │    │
│  │  ├── memory.py     (Chat history management)              │    │
│  │  ├── database.py   (Firestore operations, PDF storage)    │    │
│  │  ├── agents.py     (Calculator, Wikipedia, DuckDuckGo)    │    │
│  │  └── llm.py        (OpenRouter client)                    │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌───────────────────────────────────────────────────────────────────┐
│                      FIREBASE BACKEND                             │
│  ┌──────────────────┐         ┌──────────────────┐               │
│  │Firebase Auth     │         │Firestore DB      │               │
│  │• Secure login    │         │• Vectorstores    │               │
│  │• JWT tokens      │         │• Chat history    │               │
│  └──────────────────┘         │• User profiles   │               │
│                               │• Raw PDFs        │               │
│                               └──────────────────┘               │
└───────────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌───────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ OpenRouter   │  │ HuggingFace  │  │   FAISS      │            │
│  │ (LLM Access) │  │ (Embeddings) │  │(Vector Search│            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└───────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Query → Content Type Router
              ├─ PDF / YouTube (RAG mode)
              │    ↓
              │  Condense-Question Chain
              │    ↓
              │  Chat History (last 8 turns)
              │    ↓
              │  Standalone Query
              │    ↓
              │  FAISS Similarity Search (k=3)
              │    ↓
              │  Retrieved Chunks (returned to frontend)
              │    ↓
              │  Stuff-Docs QA Chain
              │    ↓
              │  LLM Response (via OpenRouter)
              │
              └─ CSV (Agent mode)
                   ↓
                 Pandas DataFrame Agent
                   ↓
                 Natural Language → Python Execution
                   ↓
                 Computed Result / Plot
              ↓
  Memory Update + Firestore Persist
```

---

## 🛠 Tech Stack

### Backend (server/)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI + uvicorn[standard] | Async REST API with auto docs |
| **LLM Framework** | LangChain 1.2+ (LCEL) | RAG chains, agents, memory |
| **LLM Provider** | OpenRouter | Access to 100+ models (GPT, Claude, etc.) |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Sentence encoding (384-dim vectors) |
| **Vector Store** | FAISS (faiss-cpu) | Fast similarity search (in-memory) |
| **Database** | Firebase Firestore | NoSQL for user data, chat, vectorstores, PDFs |
| **Authentication** | Firebase Admin SDK | JWT token verification |
| **Data Processing** | PyPDF, pandas, youtube-transcript-api | PDF/CSV/YouTube parsing |

### Frontend (client/)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Next.js 16.1.6 | React framework with App Router |
| **UI Library** | React 19.2.3 | Component-based UI |
| **Styling** | Tailwind CSS v4 | Utility-first CSS framework |
| **Authentication** | Firebase Client SDK | User auth state management |
| **Fonts** | Fontshare (Satoshi, Clash Display, General Sans, JetBrains Mono) | Custom typography |
| **Build Tool** | Turbopack | Fast bundler for Next.js |

---

## 📋 Prerequisites

### Required Accounts
1. **Firebase Project** ([console.firebase.google.com](https://console.firebase.google.com))
   - Enable Authentication (Email/Password provider)
   - Create a Firestore database
   - Generate a service account key (JSON) and save as `serviceAccount.json` in project root

2. **OpenRouter Account** ([openrouter.ai](https://openrouter.ai))
   - Sign up for an API key
   - Fund account (pay-as-you-go pricing)

### Required Software
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **npm or yarn** (package manager)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/omnimind.git
cd omnimind
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Download Embedding Model

The HuggingFace embedding model will auto-download on first run (~90MB). To pre-cache:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### 3. Frontend Setup

```bash
cd ../client
npm install
```

---

## ⚙ Configuration

### 1. Firebase Setup

Place your `serviceAccount.json` in the project root (`OmniMind/serviceAccount.json`).

### 2. Backend Configuration

Create `server/.env` (optional, for custom ports):

```env
PORT=8000
```

### 3. Frontend Configuration

Create `client/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

Get Firebase config from: Firebase Console → Project Settings → General → Your apps → Firebase SDK snippet

### 4. OpenRouter API Key

Users provide their own OpenRouter API keys via the Profile page (stored in Firestore per-user).

---

## 🎮 Usage

### Starting the Application

#### Terminal 1 - Backend

```bash
cd server
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at `http://localhost:8000` (API docs at `/docs`)

#### Terminal 2 - Frontend

```bash
cd client
npm run dev
```

Frontend will run at `http://localhost:3000`

### First-Time Setup

1. **Create Account**
   - Open `http://localhost:3000/login`
   - Click "Sign Up" tab
   - Enter email, password, and display name
   - Click "Sign Up"

2. **Configure API Key**
   - Navigate to Profile page
   - Enter your OpenRouter API key
   - Click "Save API Key"

### Uploading Content

OmniMind supports three content types via tabs in the Upload panel:

#### 📄 PDF Documents
1. Open the **PDF** tab in the sidebar
2. Click "Choose a PDF" and select a file
3. Click "Upload PDF"
4. Wait for processing (text extraction → chunking → embedding → Firestore storage)
5. Select the file from "Your Files" to start chatting
6. **PDF Split-View**: When a PDF is selected, the document appears on the left, chat on the right

#### 🎥 YouTube Videos
1. Open the **YouTube** tab
2. Paste a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click "Upload YouTube"
4. Transcripts are extracted, chunked, and indexed
5. File appears as `yt_{video_id}` in "Your Files"

#### 📊 CSV Files
1. Open the **CSV** tab
2. Upload a CSV file (must have headers)
3. The file is loaded into a Pandas DataFrame
4. Use natural language to query (e.g., "What's the average sales?", "Plot revenue by month")

### Chatting

1. Select a file from "Your Files" list
2. Type your question in the input box at the bottom
3. **Thinking State**: Watch the terminal-style pipeline stages as the system processes your query:
   - `[+] PARSE` - Question condensation
   - `[+] EMBED` - Vector embedding
   - `[+] SEARCH` - FAISS similarity search
   - `[+] RANK` - Relevance scoring
   - `[+] GEN` - Response generation
4. **Source Chunks**: Click the collapsible section to view retrieved document chunks with page numbers
5. **Context**: Last 8 Q&A pairs are automatically included for context-aware responses

### Autonomous Agents

If RAG can't answer (e.g., "What's 123 * 456?" or "Who won the 2024 Olympics?"), the system falls back to LangChain agents:
- **Calculator** - Math queries
- **Wikipedia** - General knowledge
- **DuckDuckGo** - Current events

---

## 📁 Project Structure

```
OmniMind/
├── server/                          # FastAPI Backend
│   ├── main.py                      # FastAPI app entry point
│   ├── middleware.py                # JWT authentication
│   ├── routes/
│   │   ├── auth.py                  # Register endpoint
│   │   ├── upload.py                # PDF/YouTube/CSV upload
│   │   ├── chat.py                  # Message endpoint
│   │   ├── files.py                 # File management, PDF serving
│   │   └── profile.py               # User profile, API key
│   ├── modules/
│   │   ├── chains.py                # LCEL-based ConversationalRAGChain
│   │   ├── rag.py                   # Vectorstore creation
│   │   ├── memory.py                # Chat history
│   │   ├── database.py              # Firestore operations
│   │   ├── agents.py                # LangChain agents
│   │   ├── llm.py                   # OpenRouter client
│   │   ├── prompts.py               # System prompts
│   │   └── theme.py                 # (Legacy, not used)
│   └── requirements.txt
│
├── client/                          # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Landing page
│   │   ├── login/
│   │   │   └── page.tsx             # Auth page
│   │   ├── chat/
│   │   │   └── page.tsx             # Main chat interface (split-view)
│   │   ├── profile/
│   │   │   └── page.tsx             # User profile
│   │   └── globals.css              # Obsidian Ember theme
│   ├── lib/
│   │   ├── firebase.ts              # Firebase client config
│   │   ├── auth-context.tsx         # Auth state management
│   │   └── api.ts                   # API client functions
│   ├── package.json
│   └── tailwind.config.ts
│
├── serviceAccount.json              # Firebase Admin SDK credentials
├── firebase.config                  # (Legacy, not used)
└── README.md
```

---

## 🧠 How It Works

### Complete RAG Pipeline

#### 1. **Document Ingestion**

When a user uploads a PDF:

```python
# Extract text
loader = PyPDFLoader(file_path)
pages = loader.load()

# Chunk with overlap
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = text_splitter.split_documents(pages)
```

**Why 1000 chars?**
- Short enough to fit in context windows
- Long enough to preserve semantic meaning
- 200-char overlap prevents context loss at boundaries

#### 2. **Embedding Generation**

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Generates 384-dimensional vectors per chunk
# Runs locally (no API costs, ~1-2s per document)
```

**Model Properties:**
- **Dimensions:** 384 (smaller = faster search)
- **Speed:** ~500 sentences/second on CPU
- **Accuracy:** 69.57 on MTEB benchmark
- **License:** Apache 2.0 (commercial-friendly)

#### 3. **Vector Storage**

```python
# Create in-memory FAISS index
vectorstore = FAISS.from_documents(chunks, embeddings)

# Serialize and chunk for Firestore
pkl = vectorstore.serialize_to_bytes()
chunks = [pkl[i:i+700KB] for i in range(0, len(pkl), 700KB)]

# Store in Firestore subcollection
users/{uid}/files/{filename}/chunks/{0,1,2,...}

# Also store raw PDF bytes
users/{uid}/files/{filename}/pdf_raw/{0,1,2,...}
```

**Why FAISS?**
- **Fast:** ~1ms for similarity search on 10K vectors
- **Efficient:** Low memory footprint
- **Portable:** Serializes to bytes for cloud storage

**Why chunk at 700KB?**
- Firestore document size limit is 1MB
- 700KB provides safety margin for metadata

#### 4. **Query Processing**

When a user asks a question, the system executes:

**Stage 1: Condense Question (if chat history exists)**

```python
# Prompt template:
Given the following conversation history and a follow-up question,
rephrase the follow-up question into a standalone question.

Chat History:
{last 8 turns}

Follow-Up Question: {user_query}
Standalone Question: [LLM output]
```

**Example:**
```
History:
  User: "What is machine learning?"
  AI: "Machine learning is a subset of AI that enables systems to learn..."

User: "How does it differ from deep learning?"

Condense Chain Output: "How does machine learning differ from deep learning?"
```

**Stage 2: Retrieval**

```python
# Embed standalone query
query_vector = embeddings.embed_query(standalone_question)

# FAISS similarity search
docs = vectorstore.similarity_search(query_vector, k=3)
# Returns top 3 most relevant chunks
```

**Stage 3: Answer Generation**

```python
# System prompt template:
You are OmniMind, a helpful and knowledgeable AI assistant.
Use the following pieces of retrieved context to answer the user's question.

Context:
{concatenated chunks from retrieval}

User: {standalone_question}
```

**Stage 4: Return to Frontend**

```json
{
  "answer": "Machine learning differs from deep learning in that...",
  "sources": [
    {
      "content": "Machine learning is a subset...",
      "page": 12,
      "source": "ml_textbook.pdf"
    },
    ...
  ]
}
```

The frontend displays the answer and shows collapsible source chunks with page numbers.

#### 5. **Memory Update**

```python
# Add Q&A pair to windowed memory
memory.save_context(
    {"question": query},
    {"answer": response}
)
# Oldest turn dropped when window size (k=8) exceeded

# Persist to Firestore
save_chat_message(user_id, file_name, "user", query)
save_chat_message(user_id, file_name, "assistant", response)
```

---

## 💾 Memory System

### Architecture

OmniMind implements a **dual-layer memory system**:

| Layer | Storage | Lifespan | Purpose |
|-------|---------|----------|---------|
| **LangChain Memory** | Backend state | Session only | Fed into chain for context-aware retrieval |
| **Display History** | Firestore | Persistent | Shown in UI, survives refresh |

### Memory Type: Windowed Message History

```python
def build_memory_from_history(history: list) -> list:
    """Convert chat history to LangChain message objects."""
    messages = []
    for msg in history[-8:]:  # Last 8 turns
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages
```

**Why windowed (not summary-based)?**

Initial implementation used `ConversationSummaryBufferMemory`, but OpenRouter-proxied models lack the `get_num_tokens_from_messages()` method required for pruning decisions. The windowed approach is simpler and doesn't require token counting.

**Per-File Isolation**

Each document gets its own chat history in Firestore:
```
users/{uid}/files/{filename}/messages/{auto-id}
```

This prevents context bleeding between different documents.

### Persistence Flow

```
New Message
    ↓
Frontend State Update (instant)
    ↓
POST /chat (backend processes)
    ↓
Firestore Write
    ↓
users/{uid}/files/{file}/messages/{auto-id}
  { role: "user", content: "...", timestamp: <server> }
```

On page reload:
```
Page Load
    ↓
GET /files/{file_name}/messages
    ↓
Load from Firestore
    ↓
Display in UI
```

---

## 📊 Data Schema

### Firestore Collections

```
users/
  {user_id}/                          # Firebase Auth UID
    ├── email: string                 # User's email address
    ├── username: string              # Display name (editable)
    ├── api_key: string               # OpenRouter API key (encrypted at rest)
    │
    └── files/
          {filename}/                 # e.g. "whitepaper.pdf", "yt_dQw4w9WgXcQ", "sales.csv"
            ├── file_name: string
            ├── content_type: string  # "pdf" | "youtube" | "csv"
            ├── total_chunks: number  # Number of FAISS binary chunks (PDF/YouTube)
            ├── total_size: number    # Original vectorstore size (bytes)
            ├── dataframe: bytes      # Pickled DataFrame (CSV only)
            ├── created_at: timestamp
            │
            ├── chunks/               # FAISS vectorstore (serialized, chunked)
            │     0/
            │       ├── data: bytes   # Binary chunk (≤700KB)
            │       └── chunk_id: number
            │     1/
            │       ├── data: bytes
            │       └── chunk_id: number
            │     ...
            │
            ├── pdf_raw/              # Raw PDF bytes (for split-view display)
            │     0/
            │       ├── data: bytes   # Binary chunk (≤700KB)
            │       └── chunk_id: number
            │     ...
            │
            └── messages/             # Chat history
                  {auto-id}/
                    ├── role: "user" | "assistant"
                    ├── content: string
                    └── timestamp: timestamp
                  ...
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by Anas**

*For questions or support, open an issue on GitHub or reach out via email.*
