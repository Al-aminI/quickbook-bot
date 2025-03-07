
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI




def get_llm(provider="gemini"):
    """
    Initialize and return an LLM based on the provider
    
    Args:
        provider: LLM provider ("gemini", "openai", or "reasoning")
    
    Returns:
        Initialized LLM
    """
    if provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="your api key")
    elif provider == "openai":
        return ChatOpenAI(model="gpt-4o-2024-05-13")
    else:  # Reasoning model
        return ChatOpenAI(model="gpt-4o")  # Less expensive than 4.5