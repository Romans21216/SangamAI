"""Stateless memory builder for FastAPI.

Reconstructs chat history as a list of LangChain message objects from
Firestore chat history on each request.  This replaces the old
ConversationBufferWindowMemory approach with a clean, modern design
compatible with LangChain v1.x.
"""

from langchain_core.messages import HumanMessage, AIMessage


def build_memory_from_history(
    chat_messages: list[dict],
    k: int = 8,
) -> list:
    """Build a list of LangChain message objects from chat messages.

    Parameters
    ----------
    chat_messages : list of dict
        ``[{"role": "user"|"assistant", "content": "..."}]`` from Firestore.
    k : int
        Number of exchange *pairs* to keep (default 8).

    Returns
    -------
    list[HumanMessage | AIMessage]
        Ready to plug into the conversational chain.
    """
    messages = []

    # Walk through messages and pair user→assistant exchanges
    i = 0
    while i < len(chat_messages) - 1:
        if (
            chat_messages[i]["role"] == "user"
            and chat_messages[i + 1]["role"] == "assistant"
        ):
            messages.append(HumanMessage(content=chat_messages[i]["content"]))
            messages.append(AIMessage(content=chat_messages[i + 1]["content"]))
            i += 2
        else:
            i += 1

    # Keep only last k pairs (2*k messages)
    if len(messages) > 2 * k:
        messages = messages[-(2 * k):]

    return messages
