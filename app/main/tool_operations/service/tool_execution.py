
from app.main.tool_operations.utils import api_call
from app.main.tool_operations.utils.prompt_helper import check_inter_tool_dependency



def execute_simple_workflow(tools_to_use, request_context):
    """
    Execute a simple sequential workflow using the original logic.
    
    Args:
        tools_to_use: List of tool objects to use
        request_context: Request context for API calls
        
    Returns:
        List of tool execution responses
    """
    tool_execution_responses = []
    previous_response = None
    
    for index, tool in enumerate(tools_to_use):
        tool_name = tool.get("tool_name", "unknown tool")
        yield f"Running {tool_name}...\n\n"
        # If there is a previous tool response and we haven't checked dependency, do so.
        if previous_response is not None:
            dependency_data = check_inter_tool_dependency(previous_response, tool)
            # Update the current tool's payload and params if dependency check returns new values.
            if dependency_data.get("updated_payload"):
                tool["payload"] = dependency_data["updated_payload"]
            if dependency_data.get("updated_params"):
                tool["params"].update(dependency_data["updated_params"])
        
        method = tool.get("method", "GET").upper()
        endpoint = tool.get("endpoint", "")
        payload = tool.get("payload", {})
        params = tool.get("params", {})
        
        if method == "GET":
            response = api_call.get_request(request_context, endpoint, params)
        elif method == "POST":
            response = api_call.post_request(request_context, endpoint, payload)
        else:
            response = None
        
        if response is not None:
            try:
                tool_response_text = response.text
            except Exception as e:
                tool_response_text = str(e)
        else:
            tool_response_text = "No response"
        
        # Save response and continue chaining for dependency checks.
        previous_response = {"tool": tool["operation"], "response": tool_response_text}
        tool_execution_responses.append(previous_response)
        
    
    yield tool_execution_responses