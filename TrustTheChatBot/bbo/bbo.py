import cma
import numpy as np
import robotic as ry


# TODO: Class inheritance from this
class BBO_ENV:

    def __init__(self):
        self.input_dim = 0

    def get_initial_state(self) -> np.ndarray:
        return np.zeros(self.input_dim)

    def compute_cost(self, params: np.ndarray) -> float:
        return 0.0

    def set_params(self, params: np.ndarray):
        pass


def compute_optimal_floats_on_code(problem: BBO_ENV,
                                   clean_code_text: str,
                                   verbose: int=0,
                                   bbo_options: dict=None) -> tuple[str, float]:
    
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
