import json
import logging

from app.main.tool_operations.service.workflow_helpers import execute_simple_workflow
# from app.main.tool_operations.utils import api_call
from app.main.tool_operations.utils.llm import call_llm, streaming_call_llm
from app.main.tool_operations.utils.memory.memory import get_or_create_memory, update_memory, reset_memory
from app.main.tool_operations.utils.prompt_helper import create_final_prompt, memory_management_prompt, tool_use_prompt
# from app.main.tool_operations.service.workflow_executor import WorkflowExecutor

logger = logging.getLogger(__name__)


def chat_handler(request_context, user_query, conversation_history=""):
    """
    Enhanced chat handler with support for complex workflows and streaming responses.
    
    Yields incremental results after completing each major operation, allowing
    for real-time updates to the client.
    """
    # get memory state
    memory_state = get_or_create_memory()
    # yield "Thinkering...\n"
    
    # Step 1: Determine the query state using Agent1
    yield "Analyzing your query...\n\n"
    agent1_prompt = memory_management_prompt(user_query, str(memory_state))
    agent1_response = call_llm(agent1_prompt)
    try:
        agent1_data = json.loads(agent1_response)
        yield "Query analysis complete.\n\n"
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Agent1 response: {agent1_response}, {e}")
        yield "Error processing the response from Agent1.\n\n"
        return
    
    # If no tool use is required, simply return the casual response.
    if not agent1_data.get("need_tool_use", False):
        casual_response = agent1_data.get("casual_response", "How can I assist you?")
        memory_state['conversation_history'] += '\nUser Request:\n' + user_query
        memory_state['conversation_history'] += '\nAgent Response:\n' + str(casual_response)
        update_memory(memory_state)
        yield casual_response
        return
    
    # Step 2: Generate the prompt for Agent2 to determine necessary tool execution.
    yield "Determining necessary tools...\n\n"
    agent2_prompt = tool_use_prompt(user_query)
    agent2_response = call_llm(agent2_prompt)
    try:
        agent2_data = json.loads(agent2_response)
        yield "Tool determination complete.\n\n"
    except json.JSONDecodeError:
        logger.error(f"Error parsing Agent2 response: {agent2_response}")
        yield "Error processing the response from Agent2.\n"
        return
    
    memory_state['conversation_history'] += '\nUser Request:\n' + user_query
    memory_state['conversation_history'] += '\nAgent Response:\n' + str(agent2_data)

    # Check if additional parameters are required before tool execution.
    if agent2_data.get("need_additional_parameters_from_user", False):
        update_memory(memory_state)
        follow_ups = agent2_data.get("follow_ups", "Additional parameters are needed to proceed.")
        yield follow_ups
        return
    
    # Get the tools and workflow description
    tools_to_use = agent2_data.get("tools", [])
    request_context = request_context
    
    # Use the original sequential tool execution for simple workflows
    yield "Executing tools...\n\n"
    tool_execution_responses = {}
    
    # Execute each tool and yield progress updates
    for tool in tools_to_use:
        tool_name = tool.get("tool_name", "unknown tool")
        yield f"Running {tool_name}...\n\n"
        
    
    tool_execution_responses = execute_simple_workflow(tools_to_use, request_context)
    yield "Tool execution complete.\n\n"
    
    # Step 4: Pass the tool execution responses to the LLM to prepare the final answer.
    yield "Preparing final response...\n\n\n"
    final_prompt = create_final_prompt(tool_execution_responses, tools_to_use, user_query)
    final_llm_response = ""
    for chunk in streaming_call_llm(final_prompt):
        yield chunk.content
        final_llm_response += chunk.content

    memory_state['conversation_history'] += '\nAgent final Response:\n' + final_llm_response

    reset_memory()
    # Step 5: Return the final response to the user.
    yield ""