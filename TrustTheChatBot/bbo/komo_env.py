import re
import ast
import numpy as np
import robotic as ry

from TrustTheChatBot.simulator import Simulator
from TrustTheChatBot.utils import str_to_np_array


class LLM_OUT_BBO_ENV_KOMO:

    def __init__(self,
                 cost_func,
                 text: str,
                 C: ry.Config,
                 scales: bool=False,
                 times: bool=False,
                 targets: bool=True,
                 features_to_be_optimized: list=[],
                 verbose: int=0
                 ):
        
        self.cost_func = cost_func
        lines = text.split("\n")
        self.objectives = []
        self.ctrl_objectives = []

        for line in lines:
            if "komo." in line:

                if "komo.addControlObjective" in line:

                    match = re.search(r'\((\[.*?\]|[^,]*),\s*([^,\s]*)\s*(?:,\s*([^)]*))?\)', line)
                    param1, param2, param3 = match.groups()

                    ctrl_objective_as_dict = {
                        "times": ast.literal_eval(param1),
                        "order": int(param2),
                        "scale": float(param3) if param3 else 1.0,                    
                    }
                    self.ctrl_objectives.append(ctrl_objective_as_dict)
                    continue
                lists = re.findall(r'\[.*?\]', line)
                params_in_objective = re.split(r',\s*(?![^\[\]]*\])', line)

                objective_as_dict = {
                    "times": str_to_np_array(lists[0]),
                    "feature": params_in_objective[1].replace(" ", ""),
                    "frames": ast.literal_eval(lists[1]),
                    "type": params_in_objective[3].replace(" ", "").replace(")", ""),
                }
                if not objective_as_dict["feature"] in ["ry.FS.accumulatedCollisions", "ry.FS.jointLimits"]:
                    objective_as_dict["scale"] = str_to_np_array(lists[2].replace(" ", "").replace(")", ""))
                    if len(lists) > 3:
                        objective_as_dict["target"] = params_in_objective[-1].replace(" ", "").replace(")", "")
                        if objective_as_dict["target"].startswith("q"):
                            objective_as_dict["target"] = np.zeros((7,))
                        else:
                            objective_as_dict["target"] = str_to_np_array(objective_as_dict["target"])

                self.objectives.append(objective_as_dict)

            elif "komo = " in line:
                init_params = line.split(",")
                self.komo_init_params = [
                    float(init_params[1]),
                    int(init_params[2]),
                    int(init_params[3]),
                    bool(init_params[-1].replace(")", ""))
                ]

        self.scales = scales
        self.times = times
        self.targets = targets
        self.features_to_be_optimized = features_to_be_optimized
        self.C = C
        self.verbose = verbose
        self.input_dim = self.get_initial_state().shape[0]
        

    def build_komo(self, C0: ry.Config) -> ry.KOMO:
        komo = ry.KOMO(C0, *self.komo_init_params)

        for ctrObj in self.ctrl_objectives:
            komo.addControlObjective(ctrObj["times"], ctrObj["order"], ctrObj["scale"])

        for obj in self.objectives:
            if not "scale" in obj.keys():
                komo.addObjective(obj["times"], eval(obj["feature"]), obj["frames"], eval(obj["type"]))
            elif not "target" in obj.keys():

                komo.addObjective(obj["times"], eval(obj["feature"]), obj["frames"], eval(obj["type"]), obj["scale"])
            else:
                komo.addObjective(obj["times"], eval(obj["feature"]), obj["frames"], eval(obj["type"]), obj["scale"], obj["target"])
        
        return komo


    def run_komo(self) -> np.ndarray:

        # TODO: Add grasping
        C2 = ry.Config()
        C2.addConfigurationCopy(self.C)
        
        komo = self.build_komo(C2)

        ret = ry.NLP_Solver(komo.nlp(), verbose=0).solve()
        q = komo.getPath()

        sim = Simulator(C2)
        xs, qs, xdots, qdots = sim.run_trajectory(q, 2, real_time=False)

        cost = self.cost_func(C2)
        del C2
        return cost
    

    def get_initial_state(self) -> tuple[np.ndarray]:
        
        initial_state = np.array([])

        for obj in self.objectives:
            if len(self.features_to_be_optimized) != 0 and obj["feature"] in self.features_to_be_optimized:

                if self.scales and "scale" in obj.keys():
                    initial_state = np.concatenate((initial_state, obj["scale"]))

                if self.times:
                    initial_state = np.concatenate((initial_state, obj["times"]))

                if self.targets and "target" in obj.keys():
                    initial_state = np.concatenate((initial_state, obj["target"]))

        return initial_state
    

    def set_params(self, params: np.ndarray):
        idx = 0
        for i, obj in enumerate(self.objectives):
            if obj["feature"] in self.features_to_be_optimized:

                if self.scales and "scale" in obj.keys():
                    size = obj["scale"].shape[0]
                    obj["scale"] = params[idx:idx+size]
                    idx += size

                if self.times:
                    size = obj["times"].shape[0]
                    obj["times"] = params[idx:idx+size]
                    idx += size
                    
                if self.targets and "target" in obj.keys():
                    size = obj["target"].shape[0]
                    obj["target"] = params[idx:idx+size]
                    idx += size
                
                self.objectives[i] = obj
    

    def compute_cost(self, params: np.ndarray) -> np.ndarray:
        self.set_params(params)
        cost = self.run_komo()
        return cost
