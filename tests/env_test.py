import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pprint import pprint
from TrustTheChatBot.utils import load_txt
from TrustTheChatBot.envs import Enviroment


# Tests
if __name__ == "__main__":
    
    env = Enviroment("bridge", "highlvl")
    
    mess = env.get_messages()
    print(mess[0]["content"][0]["text"])
    print("---")

    text = load_txt("./TrustTheChatBot/example_llm_outputs/bridge/1.txt")
    success = env.run(text)
    
    mess = env.get_messages()
    pprint(mess[-1])
    