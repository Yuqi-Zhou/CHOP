import copy
from CHOP.api import encode_image


def init_action_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful phone operating assistant. You need to help me operate the phone to complete my instruction.\n"
    operation_history.append(["user", [{"type": "text", "text": sysetm_prompt}]])
    operation_history.append(["assistant", [{"type": "text", "text": "Sure. How can I help you?"}]])
    return operation_history


def init_memory_chat():
    operation_history = []
    sysetm_prompt = "You are excellent at summarizing processes. I will provide you with the user's instruction for operating the phone and the specific execution results of each step. Please generate a summary of the overall execution result based on the user's instructions.\n"
    operation_history.append(["user", [{"type": "text", "text": sysetm_prompt}]])
    operation_history.append(["assistant", [{"type": "text", "text": "Sure. Please provide the user's instruction and the specific execution results of each step."}]])
    return operation_history


def init_split_instruction(prompt):
    instructions = []
    instructions.append(["user", [{"type": "text", "text": prompt}]])
    return instructions


def add_response(role, prompt, chat_history, image=None):
    new_chat_history = copy.deepcopy(chat_history)
    if image:
        base64_image = encode_image(image)
        content = [
            {
                "type": "text", 
                "text": prompt
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    else:
        content = [
            {
            "type": "text", 
            "text": prompt
            },
        ]
    new_chat_history.append([role, content])
    return new_chat_history