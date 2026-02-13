# SangamAI

**Where content meets clarity.**

SangamAI is a production-grade Retrieval-Augmented Generation (RAG) application that transforms PDFs, YouTube videos, and CSV datasets into interactive, conversational knowledge bases. Built with LangChain and powered by state-of-the-art language models via OpenRouter, it enables intelligent multi-modal querying with persistent chat history and context-aware responses.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)](https://python.langchain.com/)
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

---

## ✨ Features

### Core Capabilities
- **Secure Authentication** - Firebase-backed user management with email/password authentication
- **PDF Processing** - Upload and automatically index PDF documents for semantic search
- **YouTube Analysis** - Paste any YouTube URL to extract transcript, index it, and chat about the video
- **CSV Intelligence** - Upload CSV datasets and query them with natural language via a Pandas agent
- **Conversational RAG** - Ask natural language questions about your content with context-aware responses
- **Multi-Model Support** - Access GPT-4, Claude, Gemini, and Grok models through a unified interface
- **Persistent Chat History** - Conversations survive page refreshes and are stored in Firestore
- **Auto-Load Intelligence** - Vectorstores load automatically when switching between documents
- **User Profiles** - Customizable display names and saved API keys per user

### Technical Highlights
- **Multi-Modal Pipeline** - Unified RAG architecture handles PDFs, YouTube transcripts, and CSV datasets
- **Semantic Chunking** - Intelligent text splitting preserving context across 1000-character segments
- **Local Embeddings** - HuggingFace `all-MiniLM-L6-v2` runs locally (no API costs)
- **FAISS Vector Store** - High-performance similarity search with Firestore persistence
- **Pandas Agent** - Natural language querying of structured data via `langchain-experimental`
- **Conversational Memory** - Windowed memory tracks last 8 exchanges for context retention
- **Two-Stage Retrieval** - Condense-question chain + document QA chain for accurate responses

---

## 🏗 Architecture

WisdomAI implements a modular, production-ready RAG architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit Frontend                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Login View  │  │   Chat View  │  │ Profile View │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                    PDF │ YouTube │ CSV                          │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │  Auth   │ │   RAG   │ │ Agents  │ │ Memory  │ │ Chains  │    │
│  │ Module  │ │ Module  │ │ Module  │ │ Module  │ │ Module  │    │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────────┐
│                     Data & External Services                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Firestore  │  │  OpenRouter  │  │    FAISS     │           │
│  │   (NoSQL)    │  │  (LLM API)   │  │  (VectorDB)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
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
              │  Retrieved Chunks
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

### Frontend & Framework
- **[Streamlit](https://streamlit.io)** — Interactive web application framework
- **Custom CSS** — "Forge" theme with Playfair Display + Outfit typography

### Backend & Processing
- **[LangChain](https://python.langchain.com/)** — LLM orchestration framework
  - `ConversationalRetrievalChain` for RAG workflow
  - `ConversationBufferWindowMemory` for context management
  - Custom `ChatPromptTemplate`s for system prompts
- **[LangChain Experimental](https://python.langchain.com/docs/integrations/toolkits/pandas)** — Pandas DataFrame agent for CSV analysis
- **[PyPDFLoader](https://python.langchain.com/docs/integrations/document_loaders/pypdf)** — PDF parsing and extraction
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube transcript extraction
- **[RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/recursive_text_splitter)** — Intelligent text chunking

### Vector Database & Embeddings
- **[FAISS](https://github.com/facebookresearch/faiss)** (`faiss-cpu`) — Facebook AI Similarity Search
- **[HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)** — `all-MiniLM-L6-v2` (384-dim, runs locally)

### Data & Authentication
- **[Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)** — User management and authentication
- **[Google Cloud Firestore](https://firebase.google.com/docs/firestore)** — NoSQL document database for:
  - User profiles and API keys
  - Serialized FAISS vectorstores (chunked)
  - Persistent chat history

### LLM Gateway
- **[OpenRouter](https://openrouter.ai)** — Unified API gateway supporting:
  - OpenAI (GPT-4, GPT-4o-mini)
  - Anthropic (Claude Sonnet 3.7/4.5)
  - Google (Gemini 2.5/3 Flash)
  - xAI (Grok 4/4.1 Fast)

---

## 📋 Prerequisites

### Required Accounts
1. **Firebase Project** ([console.firebase.google.com](https://console.firebase.google.com))
   - Enable Authentication (Email/Password provider)
   - Create a Firestore database
   - Generate a service account key (JSON)

2. **OpenRouter Account** ([openrouter.ai](https://openrouter.ai))
   - Sign up for an API key
   - Fund account (pay-as-you-go pricing)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/omnimind.git
cd omnimind
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Embedding Model

The HuggingFace embedding model will auto-download on first run (~90MB). To pre-cache:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## ⚙ Configuration

### 1. Firebase Web API Key

Update `modules/auth.py` line 40 with your Firebase Web API key:

```python
FIREBASE_API_KEY = "AIzaSXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

Get this from: Firebase Console → Project Settings → Web API Key

### 2. OpenRouter API Key

Users provide their own OpenRouter API keys via the UI (stored in Firestore per-user). Alternatively, set a shared key in the app for single-user deployments.

---

## 🎮 Usage

### Starting the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### First-Time Setup

1. **Create Account**
   - Navigate to the "Create Account" tab
   - Enter email, password, and optional display name
   - Click "Create Account"

2. **Sign In**
   - Switch to "Sign In" tab
   - Enter credentials
   - You'll be redirected to the chat interface

3. **Configure API Key**
   - Click "Profile" in the sidebar
   - Enter your OpenRouter API key
   - Click "Save Key"

### Uploading Content

OmniMind supports three content types via tabs in the Upload panel:

#### PDF Documents
1. Open the **PDF** tab
2. Click "Choose a PDF" and select a file
3. Click "Process & Save"
4. Watch the animated pipeline:
   ```
   📄 Reading PDF pages…
   ✂️ Chunking into semantic segments…
   🔢 Generating vector embeddings…
   ☁️ Saving to cloud storage…
   ```

#### 🎥 YouTube Videos
1. Open the **🎥 YouTube** tab
2. Paste a YouTube URL (supports `youtube.com/watch?v=`, `youtu.be/`, and `embed/` formats)
3. Click "Process Video"
4. The transcript is fetched, chunked, embedded, and stored — same RAG pipeline as PDFs

#### CSV Datasets
1. Open the **CSV** tab
2. Upload a `.csv` file
3. Click "Process CSV"
4. The dataset is stored in Firestore and loaded as a Pandas DataFrame
5. Queries are handled by a natural language Pandas agent (not RAG)

### Chatting with Content

1. Switch to the **Chat** tab
2. Select content from the dropdown
3. Vectorstore (PDF/YouTube) or DataFrame (CSV) loads automatically
4. Start asking questions in natural language
5. **PDF / YouTube** → Conversational RAG with source chunks
6. **CSV** → Pandas agent executes Python to compute answers
7. Chat history persists across sessions

### Example Interactions

**PDF Chat:**
```
User: "What is the main topic of this document?"
SangamAI: Based on the content, this document focuses on...

User: "Can you elaborate on chapter 3?"
SangamAI: Chapter 3 discusses... [automatically understands context]
```

**YouTube Chat:**
```
User: "What is this video about?"
SangamAI: The video covers... [answers from transcript]

User: "What did the speaker say about AI?"
SangamAI: Around the middle of the video, the speaker mentions...
```

**CSV Chat:**
```
User: "What is the total revenue?"
SangamAI: The total revenue is $1,234,567.89

User: "Which month had the highest sales?"
SangamAI: March had the highest sales at $189,432
```

---

## Project Structure

```
sangamai/
├── app.py                      # Application entry point & routing
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── modules/                    # Core application modules
│   ├── agents.py               # Pandas DataFrame agent for CSV analysis
│   ├── auth.py                 # Firebase authentication helpers
│   ├── chains.py               # LangChain chain assembly
│   ├── database.py             # Firestore CRUD & vectorstore serialization
│   ├── llm.py                  # LLM factory for OpenRouter
│   ├── memory.py               # Conversational memory management
│   ├── prompts.py              # System, condense-question & YouTube prompts
│   ├── rag.py                  # RAG pipeline (PDF + YouTube: load, chunk, embed, retrieve)
│   └── theme.py                # CSS injection for "Forge" theme
│
└── views/                      # Streamlit page views
    ├── chat.py                 # Main chat interface (upload + chat tabs)
    ├── login.py                # Authentication page (sign in / register)
    └── profile.py              # User profile & settings
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `app.py` | Firebase initialization, session state management, page routing |
| `modules/auth.py` | User registration, password verification, username management |
| `modules/chains.py` | Wires LLM + retriever + memory into `ConversationalRetrievalChain` |
| `modules/database.py` | FAISS serialization to/from Firestore, chat history CRUD |
| `modules/llm.py` | Creates `ChatOpenAI` instances configured for OpenRouter |
| `modules/memory.py` | Per-file `ConversationBufferWindowMemory` + Firestore persistence |
| `modules/prompts.py` | Defines QA system/human prompts and condense-question prompt |
| `modules/rag.py` | PDF loading, text splitting, embedding generation, FAISS creation |
| `modules/theme.py` | Injects custom CSS for industrial-warmth aesthetic |
| `views/chat.py` | Upload tab (PDF processing), chat tab (document querying) |
| `views/login.py` | Sign in and registration forms |
| `views/profile.py` | User info display, username/API key management |

---

## How It Works

### RAG Pipeline Deep Dive

PDFs and YouTube videos share the same RAG pipeline — the only difference is the ingestion step.

#### 1. **Content Ingestion & Chunking**

**PDF path:**
```python
loader = PyPDFLoader(file_path)
docs = loader.load()  # One Document per page
chunks = splitter.split_documents(docs)
```

**YouTube path:**
```python
ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id)
transcript_text = " ".join([snippet.text for snippet in transcript])
docs = [Document(page_content=transcript_text, metadata={...})]
chunks = splitter.split_documents(docs)
```

**Shared splitter (both paths):**
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,           # ~1000 characters per chunk
    chunk_overlap=200,         # 200-char overlap for context continuity
    separators=["\n\n", "\n", ". ", " ", ""]  # Respect paragraph/sentence boundaries
)
```

**Why this approach?**
- Preserves semantic boundaries (paragraphs, sentences)
- Overlap ensures context isn't lost at chunk boundaries
- 1000 chars ≈ 250 tokens (fits well in LLM context windows)
- YouTube reuses 100% of the PDF pipeline from chunking onwards

#### 2. **Embedding Generation**

```python
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
```

**Why FAISS?**
- **Fast:** ~1ms for similarity search on 10K vectors
- **Efficient:** Low memory footprint
- **Portable:** Serializes to bytes for cloud storage

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

## Memory System

### Architecture

OmniMind implements a **dual-layer memory system**:

| Layer | Storage | Lifespan | Purpose |
|-------|---------|----------|---------|
| **LangChain Memory** | `st.session_state` | Session only | Fed into chain for context-aware retrieval |
| **Display History** | `st.session_state` + Firestore | Persistent | Shown in UI, survives refresh |

### Memory Type: ConversationBufferWindowMemory

```python
memory = ConversationBufferWindowMemory(
    k=8,                          # Keep last 8 human↔AI exchange pairs
    memory_key="chat_history",    # Key the chain reads
    return_messages=True,         # Return as Message objects (not strings)
    input_key="question",
    output_key="answer"
)
```

**Why windowed (not summary-based)?**

Initial implementation used `ConversationSummaryBufferMemory`, but OpenRouter-proxied models lack the `get_num_tokens_from_messages()` method required for pruning decisions. The windowed approach is simpler and doesn't require token counting.

**Per-File Isolation**

Each document gets its own memory instance:
```python
st.session_state[f"memory_{filename}"] = memory
st.session_state[f"messages_{filename}"] = [...]
```

This prevents context bleeding between different documents.

### Persistence Flow

```
New Message
    ↓
Session State Update (instant)
    ↓
Firestore Write (async)
    ↓
users/{uid}/files/{file}/messages/{auto-id}
  { role: "user", content: "...", timestamp: <server> }
```

On page reload:
```
Page Load
    ↓
get_chat_messages(file_name)
    ↓
Check st.session_state cache
    ↓ (if empty)
Load from Firestore
    ↓
Hydrate session state
    ↓
Render in UI
```

---

## Data Schema

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
            └── messages/             # Chat history
                  {auto-id}/
                    ├── role: "user" | "assistant"
                    ├── content: string
                    └── timestamp: timestamp
                  ...
```

### Session State Keys

```python
st.session_state = {
    "user_id": str | None,                    # Firebase UID (null if logged out)
    "page": "chat" | "profile",               # Current page
    "vectors": FAISS | None,                  # Loaded vectorstore (PDF/YouTube)
    "dataframe": DataFrame | None,            # Loaded DataFrame (CSV)
    "active_file": str | None,                # Currently selected content
    
    # Per-file memory (dynamic keys)
    "memory_{filename}": ConversationBufferWindowMemory,
    "messages_{filename}": list[dict],
}
```

---


## Security Considerations

### Authentication
- Passwords are **hashed by Firebase** (bcrypt with salt)
- API keys stored in Firestore are **encrypted at rest** by Google Cloud
- Service account credentials stored in `secrets.toml` ((not committed :) )

### Data Isolation
- Users can only access their own documents (enforced by Firestore rules)
- Session state is server-side (not exposed to client)

---

**Built with ❤️ by Anas**
