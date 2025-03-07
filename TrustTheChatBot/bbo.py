import cma
import numpy as np
import robotic as ry

from TrustTheChatBot.high_level_funcs import RobotEnviroment
import TrustTheChatBot.Robotic_Manipulation.manipulation as manip


class LLM_OUT_BBO_ENV:

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


def compute_optimal_floats_on_code(cost_func,
                                   clean_code_text: str,
                                   C: ry.Config,
                                   verbose: int=0,
                                   bbo_options: dict=None) -> tuple[str, float]:
    
    problem = LLM_OUT_BBO_ENV(cost_func, clean_code_text, C, verbose)
    
    if problem.input_dim > 0:
        
        inital_state = problem.get_initial_state()
        if bbo_options == None:
            bbo_options = {
                'popsize': 7,
                'maxiter': 50,
                'maxfevals': 5000,
                'tolfun': 1e-4,
                'tolx': 1e-5
            }
        result = cma.fmin(problem.compute_cost, inital_state, sigma0=.1, options=bbo_options)
        
        if verbose:
            print("-- BBO Result:")
            print(result[0])

        final_cost = problem.compute_cost(result[0], show=(verbose > 1))
    
        return problem.set_params(result[0]), final_cost
    
    if verbose:
        print("No floats to optimize! Returning original code.")

    return clean_code_text, 0.0
