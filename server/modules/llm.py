from langchain_openai import ChatOpenAI


def get_llm(
    api_key: str,
    model_name: str,
    temperature: float = 0,
    max_tokens: int = 1024,
) -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for OpenRouter."""
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
