import json


    
    
    
    
    
    

    
tools = None


with open('app/main/tool_operations/utils/tools/qbo_tools.json', 'r') as file:
    tools = json.load(file)

prompt = """you are giving the following tools, your task is to identify and return which tools to use in other to complete user request, make sure to return all the tools necessary to execute in order to complete user request with appropriate parameters and values and making sure that it will execute correctly. 
            your response must be in the following formart, no any additional text apart from the json object:
            {
                "tools": ["list of tools"], # like this "tools": [{"tool_name": "tool name", "operation": "operations", "description": "description of the tool"} ...] make sure to add the method, payload and extrat the exact parameters, from the query, if there are needed parameters from the user then write it in the follow_up, ensure to return the complete tool for each and it's appropriate values for each tool to call in order to completeb the user request.
                "workflow": "the workflow in explanation of how to achieve the user request by using the tools for subsequesnt agent",
                "follow_ups": "ask the user whether any additional follow-up parameters are needed to complete the tool execution. This should include a prompt to specify any extra details or settings that might be required by the tool like some parameters required in the paylload that might required from the user, ensuring that all necessary parameters are clearly defined before moving forward.",  # Note: companyId and minorversion  and authentication are handled by the system.
                  "need_additional_parameters_from_user":Boolean #True if there is need for user to provide additional parameters to complete the tool request payload else false in the follow_up. ensuring that all necessary parameters are clearly defined before moving forward
            }
            here is the user query: Which of my clients did not generate a Profit & Loss (P&L) or Balance Sheet this month?

            here is the tools set you have access to, if users query doest not require using a tool, then respond to him concisely and friendly, else make sure to outline the tools to use.
            Tools:\n""" + str(tools)
            





expected_response = {
    "tools": [
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Customer-ReadAll",
            "description": "Get all Customer objects using generic 'Query' endpoint.",
            "endpoint": "https://{{baseurl}}/v3/company/{{companyid}}/query?minorversion={{minorversion}}",
            "method": "POST",
            "payload": "Select * from Customer",
            "response": {
                "type": "array",
                "description": "Array of Customer objects",
                "items": {
                    "type": "object",
                    "description": "Customer object details",
                    "properties": {
                        "DisplayName": {
                            "type": "string",
                            "description": "Display name of the customer"
                        }
                    }
                }
            },
            "authentication": "OAuth 1.0",
            "headers": {
                "User-Agent": "Intuit-qbov3-postman-collection1",
                "Accept": "application/json",
                "Content-Type": "application/text"
            },
            "params": {
                "minorversion": "{{minorversion}}"
            }
        },
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Report-ProfitAndLoss",
            "description": "Report - Profit And Loss Method : GET",
            "endpoint": "https://{{baseurl}}/v3/company/{{companyid}}/reports/ProfitAndLoss?minorversion={{minorversion}}",
            "method": "GET",
            "payload": None,
            "response": {
                "type": "object",
                "description": "Report Details",
                "properties": {
                    "Header": {
                        "type": "object",
                        "description": "Report Header"
                    },
                    "Columns": {
                        "type": "array",
                        "description": "Column Details"
                    },
                    "Rows": {
                        "type": "array",
                        "description": "Row Details"
                    },
                    "Summary": {
                        "type": "object",
                        "description": "Report Summary"
                    }
                }
            },
            "authentication": "OAuth 1.0",
            "headers": {
                "User-Agent": "Intuit-qbov3-postman-collection1",
                "Accept": "application/json"
            },
            "params": {
                "minorversion": "{{minorversion}}"
            }
        },
        {
            "tool_name": "QuickBooks Online API",
            "operation": "Report-BalanceSheet",
            "description": "Report - Balance Sheet Method : GET",
            "endpoint": "https://{{baseurl}}/v3/company/{{companyid}}/reports/BalanceSheet?minorversion={{minorversion}}",
            "method": "GET",
            "payload": None,
            "response": {
                "type": "object",
                "description": "Report Details",
                "properties": {
                    "Header": {
                        "type": "object",
                        "description": "Report Header"
                    },
                    "Columns": {
                        "type": "array",
                        "description": "Column Details"
                    },
                    "Rows": {
                        "type": "array",
                        "description": "Row Details"
                    },
                    "Summary": {
                        "type": "object",
                        "description": "Report Summary"
                    }
                }
            },
            "authentication": "OAuth 1.0",
            "headers": {
                "User-Agent": "Intuit-qbov3-postman-collection1",
                "Accept": "application/json"
            },
            "params": {
                "minorversion": "{{minorversion}}"
            }
        }
    ],
    "workflow": "First, retrieve all customers using the Customer-ReadAll API. Then, for each customer, call both the ProfitAndLoss and BalanceSheet report APIs for this month and check if any of these generated or if both reports generated. Finally, collect all clients who did not generate a Profit & Loss (P&L) or Balance Sheet this month.",
    "follow_ups": "For the 'Report-ProfitAndLoss' and 'Report-BalanceSheet' tools, could you please specify the exact date for 'this month' so the bot can run the request correctly?",
    "need_additional_parameters_from_user": True
}