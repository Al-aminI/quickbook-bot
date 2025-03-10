# # workflow_executor.py

# import json
# import ast
# import asyncio
# import logging
# from dateutil.parser import parse
# from typing import Dict, List, Any, Optional, Union
# from ..utils import api_call
# from ..utils.llm import call_llm

# logger = logging.getLogger(__name__)

# class WorkflowExecutor:
#     """
#     A class to dynamically execute complex workflows involving multiple API calls,
#     handling dependencies between tools and processing large datasets efficiently.
#     """
    
#     def __init__(self, request_context):
#         """Initialize the workflow executor with the request context."""
#         self.request_context = request_context
#         self.execution_results = {}
#         self.tool_responses = []
    
#     def generate_executor_prompt(self, tools_to_use: List[Dict], workflow: str, user_query: str) -> str:
#         """
#         Generate a prompt for the LLM to create Python code that will execute the workflow.
        
#         Args:
#             tools_to_use: List of tool objects to be used in the workflow
#             workflow: Description of the workflow logic
#             user_query: Original user query
            
#         Returns:
#             Prompt string for the LLM
#         """
#         # Create a string representation of the tools for the prompt
#         tools_str = json.dumps(tools_to_use, indent=2)
        
#         prompt = f"""
#                     You are an expert Python developer tasked with generating code to execute a complex workflow of API calls.

#                     USER QUERY: {user_query}

#                     TOOLS TO USE:
#                     {tools_str}

#                     WORKFLOW DESCRIPTION:
#                     {workflow}

#                     Your task is to write Python code that will execute this workflow efficiently. The code should:
#                     1. Handle dependencies between API calls (where output from one call becomes input to another)
#                     2. Process large datasets efficiently
#                     3. Handle errors and edge cases gracefully
#                     4. For each data fetched or operation made that user should now, make sure to print the data with it's decscription using print statement
#                     5. Print the Final result with a print statement
#                     6. Return the final results in a structured format

#                     The generated code should use these utility functions that are already available:
#                     - api_call.get_request(request_context, endpoint, params) - For GET requests, it returns reponse object, you have to add response.json() to get the data. make sure to add the .json() when ever you call api_call.get_request
#                     - api_call.post_request(request_context, endpoint, payload) - For POST requests, it returns reponse object, you have to add response.json() to get the data. make sure to add the .json() when ever you call api_call.post_request

#                     Your response should be executable Python code (without markdown code blocks) that defines a function named `execute_workflow` that takes a `request_context` parameter and returns the final results.

#                     If the workflow requires processing each item from a large dataset, consider using async processing where appropriate to optimize performance.

#                     Additional requirements:
#                     - Validate inputs and handle potential errors
#                     - Add appropriate logging
#                     - Include detailed comments explaining the workflow logic
#                     - For any complex iteration or data processing, ensure it's memory efficient
#                     - Make sure to print the Final result with a print statement

#                     Return ONLY the Python code, without any explanation before or after.
#                     """
#         return prompt
    
#     def execute_api_call(self, tool: Dict) -> Dict[str, Any]:
#         """
#         Execute a single API call based on the tool definition.
        
#         Args:
#             tool: Tool definition including method, endpoint, payload, and params
            
#         Returns:
#             Dictionary with tool name and response
#         """
#         method = tool.get("method", "GET").upper()
#         endpoint = tool.get("endpoint", "")
#         payload = tool.get("payload", {})
#         params = tool.get("params", {})
        
#         try:
#             if method == "GET":
#                 response = api_call.get_request(self.request_context, endpoint, params)
#             elif method == "POST":
#                 response = api_call.post_request(self.request_context, endpoint, payload)
#             else:
#                 return {"tool": tool.get("operation"), "response": f"Unsupported method: {method}", "success": False}
            
#             if response is not None:
#                 try:
#                     # Try to parse as JSON first
#                     if hasattr(response, 'json'):
#                         try:
#                             response_data = response.json()
#                             response_text = json.dumps(response_data)
#                         except:
#                             response_text = response.text
#                     else:
#                         response_text = str(response)
                    
#                     return {
#                         "tool": tool.get("operation"), 
#                         "response": response_text,
#                         "success": True
#                     }
#                 except Exception as e:
#                     return {
#                         "tool": tool.get("operation"), 
#                         "response": str(e),
#                         "success": False
#                     }
#             else:
#                 return {
#                     "tool": tool.get("operation"), 
#                     "response": "No response",
#                     "success": False
#                 }
                
#         except Exception as e:
#             logger.error(f"Error executing API call: {str(e)}")
#             return {
#                 "tool": tool.get("operation"), 
#                 "response": f"Error: {str(e)}",
#                 "success": False
#             }
    
#     async def execute_generated_code(self, code: str) -> Any:
#         """
#         Execute the dynamically generated Python code for the workflow.
        
#         Args:
#             code: String containing Python code to execute
            
#         Returns:
#             Result of the workflow execution
#         """
#         try:
#             # Create a namespace for the code execution
#             namespace = {
#                 'api_call': api_call,
#                 'request_context': self.request_context,
#                 'json': json,
#                 'asyncio': asyncio,
#                 'logging': logging,
#                 'execute_api_call': self.execute_api_call
#             }
            
#             # Parse the code to check for syntax errors before executing
#             ast.parse(code)
            
#             # Execute the code
#             exec(code, namespace)
            
#             # Get the execute_workflow function from the namespace
#             if 'execute_workflow' not in namespace:
#                 raise ValueError("The generated code must define an 'execute_workflow' function")
            
#             execute_workflow = namespace['execute_workflow']
            
#             # Execute the workflow
#             results = execute_workflow(self.request_context)
#             return results
            
#         except Exception as e:
#             logger.error(f"Error executing generated workflow code: {str(e)}")
#             logger.error(f"Code that failed: {code}")
#             return {"error": str(e), "code": code}
    
#     def execute_workflow(self, tools_to_use: List[Dict], workflow: str, user_query: str) -> Dict[str, Any]:
#         """
#         Main method to execute a complex workflow.
        
#         Args:
#             tools_to_use: List of tool objects to be used in the workflow
#             workflow: Description of the workflow logic
#             user_query: Original user query
            
#         Returns:
#             Results of the workflow execution
#         """
#         # Generate the prompt for the code generation LLM
#         prompt = self.generate_executor_prompt(tools_to_use, workflow, user_query)
        
#         # Call the LLM to generate Python code
#         generated_code = call_llm(prompt)
#         if not isinstance(generated_code, str):
#             generated_code = generated_code.content
#         # Clean up the code (remove potential markdown code blocks if present)
#         if "```python" in generated_code:
#             generated_code = generated_code.split("```python")[1].split("```")[0].strip()
#         elif "```" in generated_code:
#             generated_code = generated_code.split("```")[1].split("```")[0].strip()
            
#         # Execute the generated code
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             results = loop.run_until_complete(self.execute_generated_code(generated_code))
#         finally:
#             loop.close()
            
#         # Store the tool responses for later use
#         if isinstance(results, dict) and "tool_responses" in results:
#             self.tool_responses = results["tool_responses"]
#         print("---------------------------------- execution result----------------------------\n", results)
#         return results