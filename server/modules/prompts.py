from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# ---------------------------------------------------------------------------
# QA Prompt  – used by the "stuff" docs chain inside ConversationalRetrievalChain
# Variables injected automatically:
#   {context}  – retrieved document chunks
#   {question} – the (possibly condensed) user question
# ---------------------------------------------------------------------------

_QA_SYSTEM_TEMPLATE = """\
You are SangamAI, a helpful and knowledgeable AI assistant.
Use the following pieces of retrieved context to answer the user's question.
If the context does not contain enough information, say so honestly — do not make things up.
Keep your answers clear, concise, and well-structured.

Context:
{context}"""

_QA_HUMAN_TEMPLATE = "{question}"


def get_qa_prompt() -> ChatPromptTemplate:
    """Return the prompt template used for the document-QA step."""
    return ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(_QA_SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template(_QA_HUMAN_TEMPLATE),
        ]
    )


# ---------------------------------------------------------------------------
# Condense-question Prompt – rewrites a follow-up into a standalone question
# so the retriever can find relevant chunks without needing chat history.
# Variables:
#   {chat_history} – prior conversation turns
#   {question}     – latest user message
# ---------------------------------------------------------------------------

_CONDENSE_TEMPLATE = """\
Given the following conversation history and a follow-up question, \
rephrase the follow-up question into a standalone question that captures \
the full context.
If the follow-up question is already standalone, return it as-is.

Chat History:
{chat_history}

Follow-Up Question: {question}
Standalone Question:"""


def get_condense_question_prompt() -> ChatPromptTemplate:
    """Return the prompt template for condensing follow-up questions."""
    return ChatPromptTemplate.from_template(_CONDENSE_TEMPLATE)


# ---------------------------------------------------------------------------
# YouTube Summary Prompt – generates an initial summary of the video transcript
# Variables:
#   {transcript} – full YouTube video transcript text
# ---------------------------------------------------------------------------

_YOUTUBE_SUMMARY_TEMPLATE = """\
You are SangamAI, a helpful AI assistant specialized in video content analysis.

Below is the full transcript of a YouTube video. Please provide:
1. A concise summary (2-3 paragraphs) of the main topics covered
2. Key takeaways or insights (3-5 bullet points)
3. Notable quotes or important statements (if applicable)

Keep your summary clear, objective, and well-structured.

Transcript:
{transcript}"""


def get_youtube_summary_prompt() -> ChatPromptTemplate:
    """Return the prompt template for YouTube video summarization."""
    return ChatPromptTemplate.from_template(_YOUTUBE_SUMMARY_TEMPLATE)
