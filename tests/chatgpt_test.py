import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.utils import load_txt
from TrustTheChatBot.envs import Enviroment


if __name__ == "__main__":
    
    env = Enviroment(task_name="bridge", io="highlvl", use_images=False, verbose=1)

    messages = env.get_messages()
    
    chatgpt_in = env.get_latest_message_text()
    print(chatgpt_in)
    print("---------------------------------------------")
    input("Write the ChatGPT output into './tests/chatgpt_out.txt' and press enter.")
    chatgpt_out = load_txt("./tests/chatgpt_out.txt")
    print(chatgpt_out)
    print("---------------------------------------------")
    
    success = env.run(chatgpt_out)

    env.run_solution()
    