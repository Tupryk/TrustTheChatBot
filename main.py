import json
from TrustTheChatBot.models import LLM
from TrustTheChatBot.envs import Enviroment


def main():
    
    env = Enviroment(task_name="bridge", io="highlvl", use_images=True)
    solver = LLM(model_name="Qwen7B")

    max_trial_count = 5
    for i in range(max_trial_count):

        print(f"---------------- Attempt Number {i+1} ----------------")
        messages = env.get_messages()
        text_out = solver.send(messages)
        print(text_out)
        
        success = env.run(text_out)
        if success: break
        print("Failed! Here is the enviroment feedback: ")
        print(env.get_latest_message_text())

    if success:
        print("Task was solved!")
        env.run_solution()
    else:
        print("Failed to solve task :(")
    
    json.dump(env.get_messages(), open("chat_log.json", "w"))


if __name__ == "__main__":
    main()
