"""Chain assembly — wires together the LLM, retriever, and prompts using LCEL.

Replaces the legacy ``ConversationalRetrievalChain`` with a modern
LangChain Expression Language (LCEL) pipeline that performs:

1. **Condense-question step** – rewrites the latest user message into a
   standalone question using the chat history (prompt from ``prompts.py``).
2. **Retrieve + QA step** – retrieves relevant chunks, stuffs them into
   the QA prompt (also from ``prompts.py``), and generates the answer.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from modules.prompts import get_qa_prompt, get_condense_question_prompt


def _format_docs(docs) -> str:
    """Join retrieved documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def _format_chat_history(messages: list) -> str:
    """Convert LangChain message objects to a readable string."""
    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)


class ConversationalRAGChain:
    """A simple wrapper that mimics the old ConversationalRetrievalChain interface."""

    def __init__(self, llm, retriever, chat_history: list):
        self.llm = llm
        self.retriever = retriever
        self.chat_history = chat_history

        # Build the condense-question chain
        self.condense_prompt = get_condense_question_prompt()
        self.condense_chain = (
            self.condense_prompt | self.llm | StrOutputParser()
        )

        # Build the QA chain
        self.qa_prompt = get_qa_prompt()
        self.qa_chain = self.qa_prompt | self.llm | StrOutputParser()

    def __call__(self, inputs: dict) -> dict:
        question = inputs["question"]

        # Step 1: Condense the question using chat history
        if self.chat_history:
            standalone_question = self.condense_chain.invoke({
                "chat_history": _format_chat_history(self.chat_history),
                "question": question,
            })
        else:
            standalone_question = question

        # Step 2: Retrieve relevant documents
        docs = self.retriever.invoke(standalone_question)

        # Step 3: Generate answer
        answer = self.qa_chain.invoke({
            "context": _format_docs(docs),
            "question": standalone_question,
        })

        return {
            "answer": answer,
            "source_documents": docs,
        }


def build_conversational_chain(llm, retriever, chat_history: list):
    """Return a ready-to-use conversational RAG chain.

    Parameters
    ----------
    llm : ChatOpenAI (or compatible)
    retriever : VectorStoreRetriever
    chat_history : list[HumanMessage | AIMessage]
        From ``build_memory_from_history()``
    """
    return ConversationalRAGChain(llm, retriever, chat_history)


def ask_question(chain, question: str) -> dict:
    """Run *question* through the chain and return a tidy result dict.

    Returns
    -------
    dict with keys ``"answer"`` (str) and ``"source_documents"`` (list).
    """
    result = chain({"question": question})
    return {
        "answer": result["answer"],
        "source_documents": result.get("source_documents", []),
    }
