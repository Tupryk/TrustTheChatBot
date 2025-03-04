import numpy as np
from TrustTheChatBot.code_executers import *
from TrustTheChatBot.tasks.configurations import *
from TrustTheChatBot.tasks.const_functions import *
from TrustTheChatBot.code_filters import cleanup_highlvl_func
from TrustTheChatBot.bbo import LLM_OUT_BBO_ENV, compute_optimal_floats_on_code
from TrustTheChatBot.utils import load_txt, build_message, take_picture, extract_code_block


class Enviroment:

    def __init__(self,
                 task_name: str,
                 io: str,
                 global_prompt: str="default",
                 use_images: bool=False,
                 verbose: int=0):
        
        if task_name == "bridge":
            self.C, frame_names, camera_frame = BridgeScene()
            self.cost_func = bridge_cost_func
        else:
            raise Exception(f"Task with name '{task_name}' not implemented yet!")
        
        if use_images:
            self.img_count = 1
            take_picture(self.C, camera_frame, self.img_count)
        
        if io == "highlvl":
            self.code_filter = lambda text: cleanup_highlvl_func(text)
        else:
            raise Exception(f"IO with name '{io}' not implemented yet!")

        tutorial = load_txt(f"./TrustTheChatBot/prompts/io/{io}/tutorial.txt")
        global_text = load_txt(f"./TrustTheChatBot/prompts/global/{global_prompt}.txt")
        task_description = load_txt(f"./TrustTheChatBot/prompts/tasks/{task_name}/task_description.txt")

        self.messages = []
        initial_prompt = tutorial + "\n" + global_text + "\n" + task_description + "\n"
        initial_prompt += f"Here is a list of all available object names: {frame_names}"
        initial_prompt = build_message("user", initial_prompt)
        self.messages.append(initial_prompt)
        
        self.camera_frame = camera_frame
        self.use_images = use_images
        self.solved = False
        self.verbose = verbose


    def get_messages(self) -> list:
        return self.messages
    
    
    def run(self, llm_text: str) -> bool:

        # Store LLM message
        llm_mess = build_message("system", llm_text)
        self.messages.append(llm_mess)

        # Extract code from text and clean the code
        code_text = extract_code_block(llm_text)
        code_text = self.code_filter(code_text)
        if self.verbose: print(code_text)

        # Check for errors in code
        bbo_env = LLM_OUT_BBO_ENV(self.cost_func, code_text, self.C)
        try:
            input_floats = np.zeros(bbo_env.input_dim)
            bbo_env.compute_cost(input_floats)

        except Exception as e:
            error_mess = f"There was an error in your code: {e}\nFix it."
            error_mess = build_message("user", error_mess)
            self.messages.append(error_mess)
            return False
    
        # Black Box Optimization
        final_code, final_cost = compute_optimal_floats_on_code(self.cost_func, code_text, self.C)
        if final_cost >= self.error_thresh:
            return False

        # TODO: Execute on robot
        
        if self.use_images:
            self.img_count += 1
            take_picture(self.C, self.camera_frame, self.img_count)

        return True
    
    
    def run_solution(self):
        if not self.solved:
            raise Exception("Task was not solved yet!")
        