
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
        return ChatOpenAI(model="gpt-4o-2024-05-13")
    else:  # Reasoning model
        return ChatOpenAI(model="gpt-4o")  # Less expensive than 4.5
    
    
    
# def call_llm(prompt):
#     """
#     Placeholder for an LLM call.
#     In production, this would send the prompt to an LLM service and return its response.
#     Here we simulate responses based on the prompt content.
#     """
#     if "conversation history" in prompt:
#         # Simulated response from Agent1: classify the user query.
#         return json.dumps({
#             "is_follow_up": False,
#             "need_tool_use": True,
#             "casual_response": None
#         })
#     elif "tools set you have access" in prompt:
#         # Simulated response from Agent2: determine the tools to use.
#         return json.dumps({
#             "tools": [
#                 {
#                     "tool_name": "QuickBooks Online API",
#                     "operation": "Customer-ReadAll",
#                     "description": "Get all Customer objects using generic 'Query' endpoint.",
#                     "endpoint": "/query?minorversion={{minorversion}}",  # Simplified endpoint for demonstration
#                     "method": "POST",
#                     "payload": {"query": "Select * from Customer"},
#                     "response": {},
#                     "authentication": "OAuth 1.0",
#                     "headers": {
#                         "User-Agent": "Intuit-qbov3-postman-collection1",
#                         "Accept": "application/json",
#                         "Content-Type": "application/text"
#                     },
#                     "params": {"minorversion": "14"}
#                 }
#             ],
#             "workflow": "Retrieve all customers and then filter those who did not generate the required reports.",
#             "follow_ups": "Please specify the exact month for the reports.",
#             "need_additional_parameters_from_user": False
#         })
#     else:
#         # Final LLM response assembling the tool execution responses
#         return "Here is the final response based on the tool execution results."



def call_llm(prompt):
    prompt = PromptTemplate(
        template=prompt,
    )
    
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run()
    return result