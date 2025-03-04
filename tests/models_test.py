import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.models import LLM
from TrustTheChatBot.utils import build_message


# Tests
if __name__ == "__main__":
    
    solver = LLM(model_name="Qwen7B")

    messages = []
    message = build_message("user", "How many r's are in strawberry?")
    messages.append(message)
    
    text_out = solver.send(messages)
    print(text_out)
    