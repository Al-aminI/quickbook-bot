import json


    
    
    
    
    
    

    
tools = None


with open('app/main/tools/utils/qbo_tools.json', 'r') as file:
    tools = json.load(file)
    
    
history = None
prompt = """you are giving this conversation history between user and agent, your task is to classify user prompt and identify his intent then generate you response based on that. 
            your response must be in the following formart, no any additional text apart from the json object:
            {
                "is_follow_up": Boolean # True if the user query is follow up response of the previous question by the agent requesting additional details to complete the tool, else False
                "need_tool_use": Boolean, # True if user query requires using a tool else False. Note: if user request is a casual conversation, no need to return tools, but a casual_response
                "casual_response": "if user request does not require using tool, causally anwer him with friendy tone, else this field should be null",
                
            }
            here is the user query: hello

            here is the conversation history between the user and the agent:\n""" + str(history)
            





expected_response = {
  "is_follow_up": False,
  "need_tool_use": False,
  "casual_response": "Hello! How can I help you today?"
}