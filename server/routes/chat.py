"""Chat routes — RAG (PDF/YouTube) and Pandas agent (CSV) modes."""

import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore

from middleware import get_current_user
from modules.llm import get_llm
from modules.rag import get_retriever, get_embeddings
from modules.chains import build_conversational_chain, ask_question
from modules.memory import build_memory_from_history
from modules.database import (
    load_vectorstore_from_firestore,
    load_dataframe_from_firestore,
    save_chat_message,
    load_chat_history,
    clear_chat_history,
)
from modules.agents import create_pandas_agent_chain, ask_dataframe_question

router = APIRouter()


# ── Simple in-memory vectorstore cache ────────────────────────────────
_vs_cache: dict[str, tuple] = {}
_CACHE_TTL = 600  # seconds


def _get_vectorstore_cached(user_id: str, file_name: str, embeddings):
    key = f"{user_id}:{file_name}"
    if key in _vs_cache:
        vs, ts = _vs_cache[key]
        if time.time() - ts < _CACHE_TTL:
            return vs
    vs = load_vectorstore_from_firestore(user_id, file_name, embeddings)
    if vs:
        _vs_cache[key] = (vs, time.time())
    return vs


def _invalidate_cache(user_id: str, file_name: str):
    _vs_cache.pop(f"{user_id}:{file_name}", None)


# ── Chat message endpoint ────────────────────────────────────────────

class ChatRequest(BaseModel):
    file_name: str
    question: str
    api_key: str
    model: str = "google/gemini-2.5-flash"


@router.post("/message")
async def send_message(req: ChatRequest, user_id: str = Depends(get_current_user)):
    """Send a question about a file → get AI response."""
    try:
        # Determine content type
        db = firestore.client()
        file_ref = (
            db.collection("users")
            .document(user_id)
            .collection("files")
            .document(req.file_name)
        )
        file_doc = file_ref.get()
        if not file_doc.exists:
            raise HTTPException(status_code=404, detail="File not found")

        content_type = file_doc.to_dict().get("content_type", "pdf")
        llm = get_llm(req.api_key, req.model)

        if content_type == "csv":
            # ── CSV mode (Pandas agent) ───────────────────────────
            df = load_dataframe_from_firestore(user_id, req.file_name)
            if df is None:
                raise HTTPException(status_code=404, detail="DataFrame not found")

            agent = create_pandas_agent_chain(llm, df, verbose=False)
            answer = ask_dataframe_question(agent, req.question)
        else:
            # ── RAG mode (PDF / YouTube) ──────────────────────────
            embeddings = get_embeddings()
            vectorstore = _get_vectorstore_cached(user_id, req.file_name, embeddings)
            if not vectorstore:
                raise HTTPException(status_code=404, detail="Vectorstore not found")

            retriever = get_retriever(vectorstore)

            # Rebuild memory from Firestore chat history
            history = load_chat_history(user_id, req.file_name)
            memory = build_memory_from_history(history)

            chain = build_conversational_chain(llm, retriever, memory)
            result = ask_question(chain, req.question)
            answer = result["answer"]

            # Extract source chunks for transparency
            source_chunks = []
            for doc in result.get("source_documents", []):
                chunk_text = doc.page_content[:200].strip()
                page = doc.metadata.get("page", None)
                source = doc.metadata.get("source", None)
                source_chunks.append({
                    "text": chunk_text,
                    "page": page,
                    "source": source,
                })

        # Persist both messages
        save_chat_message(user_id, req.file_name, "user", req.question)
        save_chat_message(user_id, req.file_name, "assistant", answer)

        return {"answer": answer, "sources": source_chunks if content_type != "csv" else []}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Chat history endpoints ────────────────────────────────────────────

@router.get("/{file_name}/history")
async def get_history(file_name: str, user_id: str = Depends(get_current_user)):
    """Return all chat messages for a file."""
    messages = load_chat_history(user_id, file_name)
    return {"messages": messages}


@router.delete("/{file_name}/history")
async def delete_history(file_name: str, user_id: str = Depends(get_current_user)):
    """Clear chat history for a file."""
    clear_chat_history(user_id, file_name)
    return {"message": "Chat history cleared"}
