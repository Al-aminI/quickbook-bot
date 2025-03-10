import datetime
import json

from app.main.tool_operations.utils.llm import call_llm









def memory_management_prompt(user_query, conversation_history):
    """
    Generate the prompt for Agent1 based on the user query and conversation history.
    """
    prompt = f"""The current date is {datetime.datetime.now()}.\n you are giving this conversation history between user and agent, the agent was given quickbooks online tools to use to perform every kind of opertation in order to process any kind of user request, the tools description determines it's capabilities, your task is to classify user prompt and identify his intent then generate your response based on that, your only task is to check if the user wants to perform operation with the quickbooks online return need_tool_use as True, or if it is a follow up to previous conversations with quickbooks online tools agent then return is_follow_up as True, else if it not about these two, then return a casual response.
        your response must be in the following formart, no any additional text apart from the json object, do not add any ```json  or ```, return just the json object:\n 
        {{\n 
            "is_follow_up":boolean, #true if the user query is follow up response of the previous question by the agent requesting additional details to complete the tool, else false. \n
            "need_tool_use": boolean, # true if user query requires using a tool else false. this must be tru is user asked any question that is based on quickbooks online for the subsequesnt agent to  perform the operation. Note: if user request is a casual conversation, no need to return tools, but a casual_response. \n
            "casual_response": "if user request does not require using tool, causally anwer him with friendy tone, else this field should be null",\n
        "}}\n
        Here is the user query:"""
    prompt = prompt + str(user_query) + "\n\nHere is the conversation history:\n" + str(conversation_history)
    
    return prompt


def tool_use_prompt(user_query):
    """
    Generate the prompt for Agent2 based on the user query.
    Loads the available tools from the qbo_tools.json file.
    Uses intelligent defaults and minimizes follow-up questions.
    """
    with open('app/main/tool_operations/utils/tools/qbo_tools.json', 'r') as file:
        tools = json.load(file)
    
    prompt = (
        "You are a helpful assistant that can call the provided tools."

        "The tools description determines your capabilities."
        f"The current date is {datetime.datetime.now()}.\n You are giving the following tools, your task is to identify and return which tools to use in order to complete user request, make sure to return all the tools necessary to execute in order to complete user request with appropriate parameters and values and making sure that it will execute correctly." 
        "\n\nIMPORTANT GUIDELINES FOR USER EXPERIENCE:\n"
        "1. Prioritize using defaults and inferences over asking follow-up questions which will irritate users.\n"
        "2. For date ranges: When user specifies 'this year', 'last year', 'all', etc., use intelligent defaults:\n"
        "   - 'this year' = January 1 of current year to current date\n"
        "   - 'last year' = January 1 to December 31 of previous year\n"
        "   - 'all' or 'all data' = earliest possible date to current date\n"
        "   - '2023 or so' = January 1, 2023 to December 31, 2023 or so\n"
        "   - 'Q1 2023 or so' = January 1, 2023 to March 31, 2023 or so\n"
        "3. Only set need_additional_parameters_from_user to True for truly essential missing information where defaults cannot reasonably be inferred.\n"
        "4. Put yourself in the user's shoes - what would they reasonably expect without being asked?\n"
        "\nYour response must be in the following format, no any additional text apart from the json object, do not add any ```json  or ```, return just the json object:\n"
        "{{\n"
                '"tools": ["list of tools"], # like this "tools": [{{"tool_name": "tool name", "operation": "operations", "description": "description of the tool", "endpoint" : "endpoint", "payload": "if available, all payload must have a field \'query\' for the query to execute, or it must have a key that have the exact api expected field with all the values" }} ...] make sure to add the method, payload and extract the exact parameters, from the query, if there are needed parameters from the user then write it in the follow_up, ensure to return the complete tool for each and it\'s appropriate values for each tool to call in order to complete the user request.\n'
                '"workflow": "the workflow in explanation of how to achieve the user request by using the tools for subsequent agent",\n'
                '"follow_ups": "ask the user ONLY FOR TRULY ESSENTIAL parameters that cannot be reasonably inferred. Do not ask for date ranges when the user has provided general time periods - use defaults instead.", # Note: companyId and minorversion and authentication are handled by the system.\n'
                '"need_additional_parameters_from_user": Boolean # Set to true ONLY if absolutely necessary information is missing and cannot be reasonably inferred. Default to false to minimize follow-up questions.\n'
        "}}\n"
        "Here is the user query: {user_query}\n\n"
        "Here is the tools set you have access to:\n{tools}"
    ).format(user_query=user_query, tools=json.dumps(tools))
    return prompt


def check_inter_tool_dependency(previous_response, current_tool):
    """
    Check whether the result of a previous tool execution should be used to update the current tool's parameters or payload.
    
    This function sends a prompt to the LLM with the previous tool's response and the current tool's details.
    The expected response is a JSON object with optional 'updated_payload' and 'updated_params' that override the current tool's values. no any additional text apart from the json object, do not add any ```json  or ```, return just the json object.
    """
    dependency_prompt = (
        "dependency check:\n"
        "Previous tool response: {prev_resp}\n"
        "Current tool details: {curr_tool}\n"
        "Determine if any values from the previous response need to be used as parameters or payload in the current tool. "
        "Return a JSON object with keys 'updated_payload' and 'updated_params'. If no update is needed, set the value to null."
    ).format(prev_resp=json.dumps(previous_response), curr_tool=json.dumps(current_tool))
    
    dependency_llm_response = call_llm(dependency_prompt)
    
    try:
        dependency_data = json.loads(dependency_llm_response)
    except json.JSONDecodeError:
        dependency_data = {"updated_payload": None, "updated_params": None}
    
    return dependency_data


def create_final_prompt(tool_responses, tools_used, user_request):
    """
    Create a final prompt for the LLM using the responses obtained from the tool executions.
    """
    prompt = (
        "You are a helpful assistant that can use the quickbooks online apis as tools.\n."
        "The tools description determines your capabilities.\n You output should be properly formatted markdown. with proper headings and subheadings, and your response is only text, not json or any structure output."
        f"The current date is {datetime.datetime.now()}.\n You are given the following responses from tool executions made by an agent to process user request,"
        "Based on these, prepare a final, detailed, and professional response to the user:\n"
        "User request\n: {user_request}\n"
        "Tools used\n: {tools_used}\n"
        "Tools execution result\n: {responses}\n"
        "Based on the above provided data, prepare a final, detailed, and professional response to the user."
    ).format(responses=json.dumps(tool_responses), tools_used=json.dumps(tools_used), user_request=user_request)
    return prompt





# def analyze_workflow_complexity(tools_to_use, workflow_description):
#     """
#     Generate a prompt for the LLM to analyze the complexity of a workflow.
    
#     Args:
#         tools_to_use: List of tool objects
#         workflow_description: Description of the workflow
        
#     Returns:
#         Prompt string for the LLM
#     """
#     prompt = (
#         "Analyze the following workflow description and tool list to determine its complexity:\n\n"
#         f"Tools: {json.dumps(tools_to_use)}\n\n"
#         f"Workflow: {workflow_description}\n\n"
#         "Respond with a JSON object that includes:\n"
#         "{{\n"
#         '    "is_complex": Boolean (true if the workflow requires iteration),\n'
#         '    "estimated_data_size": String (estimate of data volume: "small", "medium", "large"),\n'
#         '    "dependencies": [List of dependencies between tools, e.g., "Tool1.output -> Tool2.input"],\n'
#         '    "execution_approach": "String describing the best approach to execute this workflow"\n'
#         "}}"
#     )
#     res = call_llm(prompt)
#     try:
#         complexity = json.loads(res)
#     except json.JSONDecodeError:
#         complexity = {"is_complex": False, "requires_pagination": False, "estimated_data_size": None, "dependencies": None, "execution_approach": None}
#     return complexity

# def generate_code_execution_prompt(user_query, tools_to_use, workflow_description, template_type="standard"):
#     """
#     Generate a prompt for the LLM to create Python code to execute a workflow.
    
#     Args:
#         user_query: Original user query
#         tools_to_use: List of tool objects
#         workflow_description: Description of the workflow
#         template_type: Type of code template to generate
        
#     Returns:
#         Prompt string for the LLM
#     """
#     templates = {
#         "standard": (
#             "Given the following tools and workflow description, generate Python code to execute the workflow efficiently:\n\n"
#             f"User Query: {user_query}\n\n"
#             f"Tools: {json.dumps(tools_to_use)}\n\n"
#             f"Workflow: {workflow_description}\n\n"
#             "Your code should:\n"
#             "- Handle dependencies between API calls\n"
#             "- Handle large datasets efficiently\n"
#             "- Include error handling\n"
#             "- Return results in a structured format\n\n"
#             "Use these functions for API calls:\n"
#             "- api_call.get_request(request_context, endpoint, params)\n"
#             "- api_call.post_request(request_context, endpoint, payload)\n\n"
#             "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
#         ),
#         "pagination": (
#             "Generate Python code to handle a workflow that requires pagination through large datasets:\n\n"
#             f"User Query: {user_query}\n\n"
#             f"Tools: {json.dumps(tools_to_use)}\n\n"
#             f"Workflow: {workflow_description}\n\n"
#             "Your code should:\n"
#             "- Implement pagination logic to handle large result sets\n"
#             "- Process each page efficiently\n"
#             "- Handle dependencies between API calls\n"
#             "- Include robust error handling\n\n"
#             "Use these functions for API calls:\n"
#             "- api_call.get_request(request_context, endpoint, params)\n"
#             "- api_call.post_request(request_context, endpoint, payload)\n\n"
#             "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
#         ),
#         "batch_processing": (
#             "Generate Python code to handle a workflow that requires batch processing of multiple items:\n\n"
#             f"User Query: {user_query}\n\n"
#             f"Tools: {json.dumps(tools_to_use)}\n\n"
#             f"Workflow: {workflow_description}\n\n"
#             "Your code should:\n"
#             "- Implement batch processing to handle multiple items efficiently\n"
#             "- Consider rate limiting and performance optimization\n"
#             "- Handle dependencies between API calls\n"
#             "- Include comprehensive error handling and retry logic\n\n"
#             "Use these functions for API calls:\n"
#             "- api_call.get_request(request_context, endpoint, params)\n"
#             "- api_call.post_request(request_context, endpoint, payload)\n\n"
#             "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
#         )
#     }
    
#     return templates.get(template_type, templates["standard"])