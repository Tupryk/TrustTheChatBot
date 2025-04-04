import os
from pathlib import Path

import numpy as np
import robotic as ry
from dotenv import load_dotenv

from TrustTheChatBot.simulator import Simulator
from TrustTheChatBot.io.high_level_funcs import RobotEnviroment


load_dotenv()
REPO_PATH = Path(os.environ["REPO_PATH"])


class LLM_OUT_BBO_KOMO_SIMPLE:

    def __init__(self, cost_func, clean_code_text: str, C: ry.Config, verbose: int = 0):

        self.cost_func = cost_func
        self.original_code = clean_code_text
        self.C = C
        self.input_dim = clean_code_text.count("PLACEHOLDER_FLOAT")
        self.verbose = verbose

    def get_initial_state(self) -> np.ndarray:
        initial_state = np.zeros((self.input_dim,))
        return initial_state

    def compute_cost(self, params: list[float], show: bool = True) -> float:

        global config
        config = ry.Config()
        config.addConfigurationCopy(self.C)
        filled_code_text = self.original_code
        with open(REPO_PATH / "TrustTheChatBot" / "prompts" / "io" / "komo" / "solve_komo.txt", "r") as f:
            komo_run_text = f.read()
        full_text = filled_code_text + komo_run_text

        print(f"\nRunning the following code:\n {full_text}")

        namespace = globals().copy()
        namespace.update(locals())
        exec(full_text, namespace)
        cost = self.cost_func(config, self.verbose)
        if show:
            config.view(True)

        del config
        return cost
