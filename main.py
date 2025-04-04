import os
from pathlib import Path

from dotenv import load_dotenv
import json
from TrustTheChatBot.models import LLM, OpenAiModel
from TrustTheChatBot.envs import Enviroment


load_dotenv()
REPO_PATH = Path(os.environ['REPO_PATH'])


def main():
    
    env = Enviroment(task_name="bridge", io="komo", use_images=True, verbose=True)
    solver = OpenAiModel(model_name="gpt-4o")

    max_trial_count = 5
    for i in range(max_trial_count):

        print(f"---------------- Attempt Number {i+1} ----------------")
        messages = env.get_messages()
        # text_out = solver.send(messages)
        # Debug
        with open(REPO_PATH / "TrustTheChatBot" / "prompts" / "io" / "komo" / "dummy_response.txt", "r") as f:
            text_out = f.read()
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
