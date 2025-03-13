import json
from TrustTheChatBot.models import LLM
from TrustTheChatBot.envs import Enviroment


def main():
    
    env = Enviroment(task_name="bridge", io="highlvl", use_images=False)
    solver = LLM(model_name="Qwen7B")

    max_trial_count = 5
    for _ in range(max_trial_count):
        
        messages = env.get_messages()
        text_out = solver.send(messages)
        success = env.run(text_out)
        if success: break

    if success:
        print("Task was solved!")
        env.run_solution()
    else:
        print("Failed to solve task :(")
    
    json.dump(env.get_messages(), open("chat_log.json", "w"))


if __name__ == "__main__":
    main()
