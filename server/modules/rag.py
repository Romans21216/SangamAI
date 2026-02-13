"""RAG pipeline helpers: load → chunk → embed → store → retrieve.

Supports multiple content types:
- PDF documents (PyPDFLoader)
- YouTube videos (transcript extraction)
- Plain text (for general chunking)
"""

from functools import lru_cache

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi
import re


# ---------- Embeddings (cached once per server process) ----------

@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a singleton HuggingFace embedding model (free, runs locally)."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# ---------- Text Splitter (shared across all content types) ----------

def _get_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 200):
    """Return configured text splitter (reused across PDF, YouTube, etc.)."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


# ---------- PDF Loading & Chunking ----------

def load_and_split_pdf(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list:
    """Load a PDF and split it into overlapping text chunks.

    Uses ``RecursiveCharacterTextSplitter`` which tries paragraph → sentence →
    word boundaries in order, keeping chunks semantically coherent.
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = _get_text_splitter(chunk_size, chunk_overlap)
    return splitter.split_documents(docs)


# ---------- YouTube Transcript Loading & Chunking ----------

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def load_youtube_transcript(video_url: str) -> tuple[str, dict]:
    """Fetch YouTube video transcript.
    
    Returns
    -------
    tuple of (transcript_text, metadata)
        metadata contains: video_id, title (if available)
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {video_url}")
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        transcript_text = " ".join([snippet.text for snippet in transcript])
        
        return transcript_text, {"video_id": video_id, "source": video_url}
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {e}")


def chunk_text_documents(
    text: str,
    metadata: dict = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Chunk plain text into Document objects (reusable for any text source).
    
    Parameters
    ----------
    text : str
        Raw text content
    metadata : dict, optional
        Metadata to attach to each chunk
    chunk_size : int
        Target chunk size in characters
    chunk_overlap : int
        Overlap between consecutive chunks
        
    Returns
    -------
    list of Document objects ready for embedding
    """
    splitter = _get_text_splitter(chunk_size, chunk_overlap)
    docs = [Document(page_content=text, metadata=metadata or {})]
    return splitter.split_documents(docs)


# ---------- Vectorstore ----------

def create_vectorstore(splits) -> FAISS:
    """Embed document chunks and return a FAISS vectorstore."""
    return FAISS.from_documents(splits, get_embeddings())


def get_retriever(vectorstore: FAISS, k: int = 3):
    """Wrap a vectorstore in a retriever that returns the top-*k* chunks."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


# ---------- Convenience: full pipeline ----------

def process_pdf(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> FAISS:
    """End-to-end: PDF file → FAISS vectorstore (load → chunk → embed)."""
    splits = load_and_split_pdf(file_path, chunk_size, chunk_overlap)
    return create_vectorstore(splits)


def process_youtube(
    video_url: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> tuple[FAISS, str]:
    """End-to-end: YouTube URL → transcript → FAISS vectorstore.
    
    Returns
    -------
    tuple of (vectorstore, transcript_text)
        transcript_text is the full raw transcript for summary generation
    """
    transcript_text, metadata = load_youtube_transcript(video_url)
    splits = chunk_text_documents(transcript_text, metadata, chunk_size, chunk_overlap)
    vectorstore = create_vectorstore(splits)
    return vectorstore, transcript_text
