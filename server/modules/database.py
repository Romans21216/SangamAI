from firebase_admin import firestore
import pickle
import math


def _get_db():
    """Lazy Firestore client — only called *after* firebase_admin.initialize_app()."""
    return firestore.client()


# ══════════════════════════════════════════════════════════════════════
# VECTORSTORE  (FAISS ↔ Firestore)
# ══════════════════════════════════════════════════════════════════════

def save_vectorstore_to_firestore(user_id, file_name, vectorstore, content_type="pdf"):
    """
    Serializes FAISS index, chops it into <900KB chunks, and saves to Firestore.
    
    Parameters
    ----------
    user_id : str
    file_name : str
        Identifier for the content (e.g., filename, video ID)
    vectorstore : FAISS
    content_type : str
        One of: "pdf", "youtube", "csv" (for UI display purposes)
    """
    # 1. Serialize to Bytes
    pkl = vectorstore.serialize_to_bytes()
    total_size = len(pkl)
    
    # 2. Chunking Config (Firestore limit is 1MB, we stay safe at 700KB)
    CHUNK_SIZE = 700 * 1024 
    num_chunks = math.ceil(total_size / CHUNK_SIZE)
    
    print(f"Saving {total_size} bytes in {num_chunks} chunks...")

    # 3. Save Metadata (The "Header")
    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    doc_ref.set({
        "file_name": file_name,
        "content_type": content_type,  # NEW: track what kind of content this is
        "total_chunks": num_chunks,
        "total_size": total_size,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    # 4. Save Chunks (The "Body")
    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk_data = pkl[start:end]
        
        # Save to a sub-collection 'chunks'
        doc_ref.collection("chunks").document(str(i)).set({
            "data": chunk_data,
            "chunk_id": i
        })
    
    return True

def load_vectorstore_from_firestore(user_id, file_name, embeddings):
    """
    Downloads all chunks, stitches them back together, and loads FAISS.
    """
    from langchain_community.vectorstores import FAISS

    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    
    # 1. Get Metadata
    meta = doc_ref.get()
    if not meta.exists:
        return None
    
    num_chunks = meta.to_dict()["total_chunks"]
    
    # 2. Download & Stitch
    full_pkl = b""
    for i in range(num_chunks):
        chunk_doc = doc_ref.collection("chunks").document(str(i)).get()
        if chunk_doc.exists:
            full_pkl += chunk_doc.to_dict()["data"]
            
    # 3. Deserialize
    vectorstore = FAISS.deserialize_from_bytes(
        embeddings=embeddings, 
        serialized=full_pkl,
        allow_dangerous_deserialization=True
    )
    return vectorstore


# ══════════════════════════════════════════════════════════════════════
# RAW PDF STORAGE  (for PDF viewer)
# ══════════════════════════════════════════════════════════════════════
# Path: users/{user_id}/files/{file_name}/pdf_raw/{chunk_id}

def save_pdf_bytes(user_id: str, file_name: str, raw_bytes: bytes):
    """Save raw PDF bytes to Firestore in chunks (for later viewing)."""
    CHUNK_SIZE = 700 * 1024
    num_chunks = math.ceil(len(raw_bytes) / CHUNK_SIZE)
    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    doc_ref.update({"pdf_size": len(raw_bytes), "pdf_chunks": num_chunks})
    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        chunk_data = raw_bytes[start:start + CHUNK_SIZE]
        doc_ref.collection("pdf_raw").document(str(i)).set({"data": chunk_data, "chunk_id": i})


def load_pdf_bytes(user_id: str, file_name: str) -> bytes | None:
    """Reconstruct raw PDF bytes from Firestore chunks."""
    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    meta = doc_ref.get()
    if not meta.exists:
        return None
    data = meta.to_dict()
    num_chunks = data.get("pdf_chunks", 0)
    if num_chunks == 0:
        return None
    full = b""
    for i in range(num_chunks):
        chunk_doc = doc_ref.collection("pdf_raw").document(str(i)).get()
        if chunk_doc.exists:
            full += chunk_doc.to_dict()["data"]
    return full


# ══════════════════════════════════════════════════════════════════════
# CHAT HISTORY  (Firestore-persistent)
# ══════════════════════════════════════════════════════════════════════
# Path: users/{user_id}/files/{file_name}/messages/{auto-id}
# Each doc: { role: "user"|"assistant", content: str, timestamp: server }

def save_chat_message(user_id: str, file_name: str, role: str, content: str) -> None:
    """Persist a single chat message to Firestore."""
    db = _get_db()
    msgs_ref = (
        db.collection("users")
        .document(user_id)
        .collection("files")
        .document(file_name)
        .collection("messages")
    )
    msgs_ref.add({
        "role": role,
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })


def load_chat_history(user_id: str, file_name: str) -> list[dict]:
    """Load all chat messages for a file, ordered by timestamp (oldest first).

    Returns a list of ``{"role": ..., "content": ...}`` dicts.
    """
    db = _get_db()
    msgs_ref = (
        db.collection("users")
        .document(user_id)
        .collection("files")
        .document(file_name)
        .collection("messages")
        .order_by("timestamp")
    )
    return [
        {"role": doc.to_dict()["role"], "content": doc.to_dict()["content"]}
        for doc in msgs_ref.stream()
    ]


def clear_chat_history(user_id: str, file_name: str) -> None:
    """Delete all chat messages for a file from Firestore."""
    db = _get_db()
    msgs_ref = (
        db.collection("users")
        .document(user_id)
        .collection("files")
        .document(file_name)
        .collection("messages")
    )
    # Firestore doesn't support collection-level delete — delete doc by doc
    for doc in msgs_ref.stream():
        doc.reference.delete()


# ══════════════════════════════════════════════════════════════════════
# CSV / DATAFRAME STORAGE  (Pandas DataFrame ↔ Firestore)
# ══════════════════════════════════════════════════════════════════════
# CSVs are stored as pickled DataFrames (simpler than chunking for structured data)

def save_dataframe_to_firestore(user_id: str, file_name: str, dataframe) -> None:
    """Save a Pandas DataFrame to Firestore as a pickled blob.
    
    Parameters
    ----------
    user_id : str
    file_name : str
        CSV filename or identifier
    dataframe : pd.DataFrame
    """
    import pickle
    
    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    
    # Pickle the DataFrame
    df_bytes = pickle.dumps(dataframe)
    
    doc_ref.set({
        "file_name": file_name,
        "content_type": "csv",
        "size": len(df_bytes),
        "shape": dataframe.shape,  # (rows, cols) for UI display
        "columns": list(dataframe.columns),
        "dataframe": df_bytes,  # Store pickled DF directly (if <1MB, else chunk it)
        "created_at": firestore.SERVER_TIMESTAMP
    })


def load_dataframe_from_firestore(user_id: str, file_name: str):
    """Load a Pandas DataFrame from Firestore.
    
    Returns
    -------
    pd.DataFrame or None if not found
    """
    import pickle
    
    db = _get_db()
    doc_ref = db.collection("users").document(user_id).collection("files").document(file_name)
    doc = doc_ref.get()
    
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    if data.get("content_type") != "csv":
        return None
    
    df_bytes = data.get("dataframe")
    return pickle.loads(df_bytes) if df_bytes else None