import datetime
import json

from app.main.tool_operations.utils.llm import call_llm










def memory_management_prompt(user_query, conversation_history):
    """
    Generate the prompt for Agent1 based on the user query and conversation history.
    """
    prompt = f"""The current date is {datetime.datetime.now()}.

    You are analyzing a conversation between a user and an agent with access to QuickBooks Online tools. Your task is to carefully examine the user's current query in relation to the conversation history to determine:

    1. If the current query is a follow-up to a previous exchange
    2. If the current query requires using QuickBooks Online tools
    3. if the current query can be answered from the past tool execution response without using any tool.

    IMPORTANT ANALYSIS GUIDELINES:
    - Examine both the current query AND prior conversation context
    - Look for references to previous questions (pronouns like "it", "that", "those", or implicit context)
    - Consider if the user is providing additional information requested by the agent in a previous message
    - Check if the query relates to QuickBooks data, accounts, transactions, reports, or operations
    - A query can be BOTH a follow-up AND require tool use (these are not mutually exclusive)

    For example, if the agent previously asked "Which account would you like to check?" and the user responds "The marketing expense account", this is a follow-up AND requires tool use.

    Your response must be a JSON object with EXACTLY this format (no additional text, no markdown formatting):
    {{
        "is_follow_up": boolean, 
        "need_tool_use": boolean,
        "no_tool_use_response": string or null
    }}

    Where:
    - "is_follow_up": true if the query continues or responds to a previous exchange
    - "need_tool_use": true if QuickBooks tools are needed to fulfill the request
    - "no_tool_use_response": provide a very professional detailed answer with proper headings and subheadings in markdown format when there is no need for tool use, and if the current query is follow up, make sure to accuratly answer the query from teh conversation history and the previous tools execution response, if there is no cunversation history, then answer user query accordingly; otherwise null

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
        "The tools description determines your capabilities.\n "
        "You output should be properly formatted markdown. "
        "with proper headings and subheadings, and your response is only text, not json or any structure output."
        f"The current date is {datetime.datetime.now()}.\n"
        "You are given the following responses from tool executions made by an agent to process user request,"
        "Based on these, prepare a final, detailed, and professional response to the user:\n"
        "User request\n: {user_request}\n"
        "Tools used\n: {tools_used}\n"
        "Tools execution result\n: {responses}\n"
        "Based on the above provided data, prepare a final, detailed, and professional response to the user."
    ).format(responses=json.dumps(tool_responses), tools_used=json.dumps(tools_used), user_request=user_request)
    return prompt

