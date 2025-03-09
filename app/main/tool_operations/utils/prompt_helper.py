import json

from app.main.tool_operations.utils.llm import call_llm









def generate_agent1_prompt(user_query, conversation_history):
    """
    Generate the prompt for Agent1 based on the user query and conversation history.
    """
    prompt = """you are giving this conversation history between user and agent, the agent was given quickbooks online tools to use to perform every kind of opertation in order to process any kind of user request, your task is to classify user prompt and identify his intent then generate you response based on that.
        your response must be in the following formart, no any additional text apart from the json object, do not add any ```json  or ```, return just the json object:\n 
        {{\n 
            "is_follow_up": Boolean, # True if the user query is follow up response of the previous question by the agent requesting additional details to complete the tool, else False. \n
            "need_tool_use": Boolean, # True if user query requires using a tool else False. Note: if user request is a casual conversation, no need to return tools, but a casual_response. \n
            "casual_response": "if user request does not require using tool, causally anwer him with friendy tone, else this field should be null",\n
        "}}\n
        Here is the user query:"""
    prompt = prompt + str(user_query) + "\n\nHere is the conversation history:\n" + str(conversation_history)
    
    return prompt





def generate_agent2_prompt(user_query):
    """
    Generate the prompt for Agent2 based on the user query.
    Loads the available tools from the qbo_tools.json file.
    """
    with open('app/main/tool_operations/utils/tools/qbo_tools.json', 'r') as file:
        tools = json.load(file)
    
    prompt = (
        "you are giving the following tools, your task is to identify and return which tools to use in other to complete user request, make sure to return all the tools necessary to execute in order to complete user request with appropriate parameters and values and making sure that it will execute correctly." 
        "your response must be in the following formart, no any additional text apart from the json object, do not add any ```json  or ```, return just the json object:\n"
        "{{\n"
                '"tools": ["list of tools"], # like this "tools": [{{"tool_name": "tool name", "operation": "operations", "description": "description of the tool"}} ...] make sure to add the method, payload and extrat the exact parameters, from the query, if there are needed parameters from the user then write it in the follow_up, ensure to return the complete tool for each and it\'s appropriate values for each tool to call in order to completeb the user request.\n'
                '"workflow": "the workflow in explanation of how to achieve the user request by using the tools for subsequesnt agent",\n'
                '"follow_ups": "ask the user whether any additional follow-up parameters are needed to complete the tool execution. This should include a prompt to specify any extra details or settings that might be required by the tool like some parameters required in the paylload that might required from the user, ensuring that all necessary parameters are clearly defined before moving forward.",  # Note: companyId and minorversion  and authentication are handled by the system.\n'
                '"need_additional_parameters_from_user":Boolean #True if there is need for user to provide additional parameters to complete the tool request payload else false in the follow_up. ensuring that all necessary parameters are clearly defined before moving forward.\n'
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
        "You are given the following responses from tool executions made by an agent to process user request,"
        "Based on these, prepare a final, friendly, and professional response to the user:\n"
        "User request\n: {user_request}\n"
        "Tools used\n: {tools_used}\n"
        "Tools execution result\n: {responses}\n"
        "Based on these, prepare a final, friendly, and professional response to the user."
    ).format(responses=json.dumps(tool_responses), tools_used=json.dumps(tools_used), user_request=user_request)
    return prompt





def analyze_workflow_complexity(tools_to_use, workflow_description):
    """
    Generate a prompt for the LLM to analyze the complexity of a workflow.
    
    Args:
        tools_to_use: List of tool objects
        workflow_description: Description of the workflow
        
    Returns:
        Prompt string for the LLM
    """
    prompt = (
        "Analyze the following workflow description and tool list to determine its complexity:\n\n"
        f"Tools: {json.dumps(tools_to_use)}\n\n"
        f"Workflow: {workflow_description}\n\n"
        "Respond with a JSON object that includes:\n"
        "{{\n"
        '    "is_complex": Boolean (true if the workflow requires iteration, pagination, or processing large datasets),\n'
        '    "requires_pagination": Boolean (true if the workflow might need to handle paginated results),\n'
        '    "estimated_data_size": String (estimate of data volume: "small", "medium", "large"),\n'
        '    "dependencies": [List of dependencies between tools, e.g., "Tool1.output -> Tool2.input"],\n'
        '    "execution_approach": "String describing the best approach to execute this workflow"\n'
        "}}"
    )
    res = call_llm(prompt)
    try:
        complexity = json.loads(res)
    except json.JSONDecodeError:
        complexity = {"is_complex": False, "requires_pagination": False, "estimated_data_size": None, "dependencies": None, "execution_approach": None}
    return complexity

def generate_code_execution_prompt(user_query, tools_to_use, workflow_description, template_type="standard"):
    """
    Generate a prompt for the LLM to create Python code to execute a workflow.
    
    Args:
        user_query: Original user query
        tools_to_use: List of tool objects
        workflow_description: Description of the workflow
        template_type: Type of code template to generate
        
    Returns:
        Prompt string for the LLM
    """
    templates = {
        "standard": (
            "Given the following tools and workflow description, generate Python code to execute the workflow efficiently:\n\n"
            f"User Query: {user_query}\n\n"
            f"Tools: {json.dumps(tools_to_use)}\n\n"
            f"Workflow: {workflow_description}\n\n"
            "Your code should:\n"
            "- Handle dependencies between API calls\n"
            "- Handle large datasets efficiently\n"
            "- Include error handling\n"
            "- Return results in a structured format\n\n"
            "Use these functions for API calls:\n"
            "- api_call.get_request(request_context, endpoint, params)\n"
            "- api_call.post_request(request_context, endpoint, payload)\n\n"
            "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
        ),
        "pagination": (
            "Generate Python code to handle a workflow that requires pagination through large datasets:\n\n"
            f"User Query: {user_query}\n\n"
            f"Tools: {json.dumps(tools_to_use)}\n\n"
            f"Workflow: {workflow_description}\n\n"
            "Your code should:\n"
            "- Implement pagination logic to handle large result sets\n"
            "- Process each page efficiently\n"
            "- Handle dependencies between API calls\n"
            "- Include robust error handling\n\n"
            "Use these functions for API calls:\n"
            "- api_call.get_request(request_context, endpoint, params)\n"
            "- api_call.post_request(request_context, endpoint, payload)\n\n"
            "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
        ),
        "batch_processing": (
            "Generate Python code to handle a workflow that requires batch processing of multiple items:\n\n"
            f"User Query: {user_query}\n\n"
            f"Tools: {json.dumps(tools_to_use)}\n\n"
            f"Workflow: {workflow_description}\n\n"
            "Your code should:\n"
            "- Implement batch processing to handle multiple items efficiently\n"
            "- Consider rate limiting and performance optimization\n"
            "- Handle dependencies between API calls\n"
            "- Include comprehensive error handling and retry logic\n\n"
            "Use these functions for API calls:\n"
            "- api_call.get_request(request_context, endpoint, params)\n"
            "- api_call.post_request(request_context, endpoint, payload)\n\n"
            "Your code should define a function named 'execute_workflow' that takes a request_context parameter."
        )
    }
    
    return templates.get(template_type, templates["standard"])