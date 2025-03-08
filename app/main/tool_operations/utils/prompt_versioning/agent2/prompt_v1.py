import json






tools = None



with open('app/main/tools/utils/qbo_tools.json', 'r') as file:
    tools = json.load(file)

prompt = """you are giving the following tools, your task is to identify and return which tools to use in other to complete user request, make sure to return all the tools necessary to execute in order to complete user request with appropriate parameters and values and making sure that it will execute correctly. 

            here is the user query: Which of my clients did not generate a Profit & Loss (P&L) or Balance Sheet this month?

            here is the tools set you have access to, if users query doest not require using a tool, then respond to him concisely and friendly, else make sure to outline the tools to use.
            Tools:\n""" + str(tools)
            





expected_response = """To fulfill your request, I need to use the following tools in order to identify clients without Profit & Loss (P&L) or Balance Sheet generation this month:

                        Tool: QuickBooks Online API

                        Operation: Report-ProfitAndLoss

                        Description: Retrieve Profit and Loss reports for each client.

                        Parameters:

                        minorversion: (Use the appropriate minorversion for your QBO account)

                        Tool: QuickBooks Online API

                        Operation: Report-BalanceSheet

                        Description: Retrieve Balance Sheet reports for each client.

                        Parameters:

                        minorversion: (Use the appropriate minorversion for your QBO account)

                        Tool: QuickBooks Online API

                        Operation: Customer-ReadAll

                        Description: Retrieve all Customer objects to ensure all clients are checked

                        Parameters:

                        minorversion: (Use the appropriate minorversion for your QBO account)

                        After running these API calls in the correct order, I will be able to determine which clients have not generated the reports you specified, and then return that information."""


