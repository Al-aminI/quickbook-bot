import json


    
    
    
    
    
    

    
tools = None


with open('app/main/tool_operations/utils/tools/qbo_tools.json', 'r') as file:
    tools = json.load(file)
    
    
history = """
User:\n Which of my clients did not generate a Profit & Loss (P&L) or Balance Sheet this month?\n
Agent:\n {
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
"""
prompt = """you are giving this conversation history between user and agent, your task is to classify user prompt and identify his intent then generate you response based on that. 
            your response must be in the following formart, no any additional text apart from the json object:
            {
                "is_follow_up": Boolean # True if the user query is follow up response of the previous question by the agent requesting additional details to complete the tool, else False
                "need_tool_use": Boolean, # True if user query requires using a tool else False. Note: if user request is a casual conversation, no need to return tools, but a casual_response
                "casual_response": "if user request does not require using tool, causally anwer him with friendy tone, else this field should be null",
                
            }
            here is the user query: good morning

            here is the conversation history between the user and the agent:\n""" + str(history)
            





expected_response = {
  "is_follow_up": False,
  "need_tool_use": False,
  "casual_response": "Good morning to you too!"
}