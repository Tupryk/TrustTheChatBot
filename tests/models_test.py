import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.models import LLM
from TrustTheChatBot.utils import build_message


# Tests
if __name__ == "__main__":
    
    solver = LLM(model_name="Qwen7B")

    messages = []
    message = build_message("user", "The task for the robot was to build a bridge. Was the task solved correctly?", "./tests/test_images/rescaled/bridge_success.jpg")
    messages.append(message)
    
    text_out = solver.send(messages)
    print(text_out)
    