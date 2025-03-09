import json
import os







def get_or_create_memory():
    if not os.path.exists('app/main/tool_operations/utils/memory/memory.json'):
        # If the file doesn't exist, create it with an empty dictionary
        with open('app/main/tool_operations/utils/memory/memory.json', 'w') as f:
            json.dump({"conversation_history":""}, f)
        return {}
    else:
        # If the file exists, load and return its content
        with open('app/main/tool_operations/utils/memory/memory.json', 'r') as f:
            memory_state = json.load(f)
        return memory_state



def update_memory(memory_state):
    # Update (or create) the app/main/tool_operations/utils/memory/memory.json file with the current memory state
    with open('app/main/tool_operations/utils/memory/memory.json', 'w') as f:
        json.dump(memory_state, f, indent=4)