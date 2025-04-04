import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.utils import load_txt
from TrustTheChatBot.tasks.configurations import BeerScene
from TrustTheChatBot.code_filters import cleanup_highlvl_func
from TrustTheChatBot.io.high_level_funcs import RobotEnviroment




if __name__ == "__main__":

    C, _, _ = BeerScene()
    C.view(True)

    raw_out = load_txt("./TrustTheChatBot/example_llm_outputs/beer/1.txt")
    clean_text = cleanup_highlvl_func(raw_out, visuals=True)
    print(clean_text)
    exec(clean_text)