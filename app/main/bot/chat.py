import json
import logging

from app.main.tool_operations.service.workflow_helpers import execute_simple_workflow
from app.main.tool_operations.utils import api_call
from app.main.tool_operations.utils.llm import call_llm
from app.main.tool_operations.utils.prompt_helper import analyze_workflow_complexity, create_final_prompt, generate_agent1_prompt, generate_agent2_prompt
from app.main.tool_operations.service.workflow_executor import WorkflowExecutor

logger = logging.getLogger(__name__)

def chat_handler(request_context, user_query, conversation_history=""):
    """
    Enhanced chat handler with support for complex workflows.
    
    Flow:
    1. Get the user query and use Agent1 to classify intent.
    2. If the query does not require a tool, return a casual response.
    3. If a tool is needed, use Agent2 to determine the tools and workflow.
    4. If additional parameters are required, return a follow-up prompt.
    5. Analyze the workflow complexity:
       a. For simple sequential workflows, use the original tool execution logic.
       b. For complex workflows with iterations or dependencies, use the WorkflowExecutor.
    6. Pass the tool execution responses to the LLM to prepare the final answer,
       and return that response to the user.
    """
    # Step 1: Determine the query state using Agent1
    agent1_prompt = generate_agent1_prompt(user_query, conversation_history)
    agent1_response = call_llm(agent1_prompt)
    try:
        agent1_data = json.loads(agent1_response)
    except json.JSONDecodeError:
        logger.error(f"Error parsing Agent1 response: {agent1_response}")
        return "Error processing the response from Agent1."
    
    # If no tool use is required, simply return the casual response.
    if not agent1_data.get("need_tool_use", False):
        return agent1_data.get("casual_response", "How can I assist you?")
    
    # Step 2: Generate the prompt for Agent2 to determine necessary tool execution.
    agent2_prompt = generate_agent2_prompt(user_query)
    agent2_response = call_llm(agent2_prompt)
    try:
        agent2_data = json.loads(agent2_response)
    except json.JSONDecodeError:
        logger.error(f"Error parsing Agent2 response: {agent2_response}")
        return "Error processing the response from Agent2."
    
    # Check if additional parameters are required before tool execution.
    if agent2_data.get("need_additional_parameters_from_user", False):
        return agent2_data.get("follow_ups", "Additional parameters are needed to proceed.")
    
    # Get the tools and workflow description
    tools_to_use = agent2_data.get("tools", [])
    workflow_description = agent2_data.get("workflow", "")
    request_context = request_context
    
    # Step 3: Determine workflow complexity and execute accordingly
    # is_complex_workflow = determine_workflow_complexity(workflow_description, tools_to_use)
    is_complex_workflow = analyze_workflow_complexity(workflow_description, tools_to_use)
    
    if is_complex_workflow['is_complex']:
        # Use the dynamic workflow executor for complex workflows
        executor = WorkflowExecutor(request_context)
        execution_results = executor.execute_workflow(tools_to_use, workflow_description + is_complex_workflow['dependencies'] + is_complex_workflow["execution_approach"], user_query)
        
        # Handle potential errors in the execution
        if isinstance(execution_results, dict) and "error" in execution_results:
            logger.error(f"Error in workflow execution: {execution_results['error']}")
            return f"There was an error processing your request: {execution_results['error']}"
        
        # Use the tool responses collected by the executor
        tool_execution_responses = executor.tool_responses
    else:
        # Use the original sequential tool execution for simple workflows
        tool_execution_responses = execute_simple_workflow(tools_to_use, request_context)
    
    # Step 4: Pass the tool execution responses to the LLM to prepare the final answer.
    final_prompt = create_final_prompt(tool_execution_responses, tools_to_use, user_query)
    final_llm_response = call_llm(final_prompt)
    
    # Step 5: Return the final response to the user.
    return final_llm_response
