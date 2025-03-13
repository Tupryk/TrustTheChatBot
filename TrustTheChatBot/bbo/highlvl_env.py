import numpy as np
import robotic as ry

from TrustTheChatBot.io.high_level_funcs import RobotEnviroment


class LLM_OUT_BBO_ENV_HIGHLVL:

    def __init__(self, cost_func, clean_code_text: str, C: ry.Config, verbose: int=0):
        
        self.cost_func = cost_func
        self.original_code = clean_code_text
        self.C = C
        self.input_dim = clean_code_text.count("PLACEHOLDER_FLOAT")
        self.verbose = verbose
        
    
    def get_initial_state(self) -> np.ndarray:
        initial_state = np.zeros((self.input_dim,))
        return initial_state
    
    
    def set_params(self, params: list[float]) -> str:
        filled_code_text = str(self.original_code)
        for value in params:
            filled_code_text = filled_code_text.replace("PLACEHOLDER_FLOAT", str(value), 1)
        return filled_code_text

    
    def compute_cost(self, params: list[float], show: bool=False) -> float:
        
        global C_copy
        C_copy = ry.Config()
        C_copy.addConfigurationCopy(self.C)
        filled_code_text = self.set_params(params)
        filled_code_text = filled_code_text.replace("(C,", "(C_copy,")

        exec(filled_code_text, globals(), locals())
        cost = self.cost_func(C_copy, self.verbose)
        if show:
            C_copy.view(True)
        
        del C_copy
        return cost
    