import json


    
    
    
    
    
    

    
tools = None


with open('app/main/tools/utils/qbo_tools.json', 'r') as file:
    tools = json.load(file)

prompt = """you are giving the following tools, your task is to identify and return which tools to use in other to complete user request, make sure to return all the tools necessary to execute in order to complete user request with appropriate parameters and values and making sure that it will execute correctly. 
            your response must be in the following formart, no any additional text apart from the json object:
            {
                "tools": ["list of tools"], # like this "tools": [{"tool_name": "tool name", "operation": "operations", "description": "description of the tool"}]
                "workflow": "the workflow in explanation of how to achieve the user request by using the tools for subsequesnt agent",
                "follow_ups": "ay additional follow up to ask the user before proceeding with the execution, like additional details in the parameter according to the tool that is needed to be specified by the user",   
            }
            here is the user query: Which of my clients did not generate a Profit & Loss (P&L) or Balance Sheet this month?

            here is the tools set you have access to, if users query doest not require using a tool, then respond to him concisely and friendly, else make sure to outline the tools to use.
            Tools:\n""" + str(tools)
            





expected_response = {
    "tools": [
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Customer-ReadAll",
            "description": "Get all Customer objects using generic 'Query' endpoint."
        },
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Report-ProfitAndLoss",
            "description": "Report - Profit And Loss Method : GET"
        },
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Report-BalanceSheet",
            "description": "Report - Balance Sheet Method : GET"
        }
    ],
    "workflow": "1. Use 'Customer-ReadAll' to get a list of all customers. \n2. For each customer, use 'Report-ProfitAndLoss' and 'Report-BalanceSheet' to see if a report was generated this month.\n3. Return the names of customers for which either 'ProfitAndLoss' or 'BalanceSheet' was not generated this month.",
    "follow_ups": "I need the company ID and minorversion to execute the calls to QuickBooks Online API. Also, could you clarify the exact date range for \"this month\" for generating the Profit & Loss and Balance Sheet reports? Finally, do you have a specific currency that you would like to see this report in?",
}