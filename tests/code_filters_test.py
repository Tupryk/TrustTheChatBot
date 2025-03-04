import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.utils import load_txt
from TrustTheChatBot.code_filters import *


# Tests
if __name__ == "__main__":
    
    print("--------------------------- High lvl ---------------------------")
    raw_text = load_txt("./TrustTheChatBot/example_llm_outputs/bridge/1.txt")
    clean_text = cleanup_highlvl_func(raw_text)
    print(clean_text)