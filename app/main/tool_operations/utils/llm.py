
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from app.main import config




def get_llm(provider="gemini"):
    """
    Initialize and return an LLM based on the provider
    
    Args:
        provider: LLM provider ("gemini", "openai", or "reasoning")
    
    Returns:
        Initialized LLM
    """
    if provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=config.GOOGLE_AI_API_KEY)
    elif provider == "openai":
        return ChatOpenAI(model="gpt-4o-2024-05-13", api_key=config.OPEN_AI_API_KEY)
    else:  # Reasoning model
        return ChatOpenAI(model="gpt-4o")  # Less expensive than 4.5
    
   


def call_llm(prompt): 
    llm = get_llm()
    result = llm.invoke(prompt)
    # Clean up the code (remove potential markdown code blocks if present)
    if "```json" in result.content:
        result = result.content.split("```json")[1].split("```")[0].strip()
   
    elif "```markdown" in result.content:
        result = result.content.split("```json")[1].split("```")[0].strip()

    elif "```" in result:
        result = result.content.split("```")[1].split("```")[0].strip()

    else:
        result = result.content
    print("data", result)
    return result



def streaming_call_llm(prompt): 
    llm = get_llm()
    
    for chunk in llm.stream(prompt):
        yield chunk