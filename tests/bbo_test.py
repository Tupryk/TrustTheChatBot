import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.utils import load_txt
from TrustTheChatBot.tasks.configurations import BridgeScene
from TrustTheChatBot.code_filters import cleanup_highlvl_func
from TrustTheChatBot.bbo import compute_optimal_floats_on_code
from TrustTheChatBot.tasks.const_functions import bridge_cost_func


if __name__ == "__main__":

    C, _, _ = BridgeScene()

    raw_out = load_txt("./TrustTheChatBot/example_llm_outputs/bridge/1.txt")
    clean_text = cleanup_highlvl_func(raw_out)
    
    optimal_code = compute_optimal_floats_on_code(bridge_cost_func, clean_text, C, verbose=2)
    print(optimal_code)
    