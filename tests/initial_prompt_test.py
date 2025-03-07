import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.envs import Enviroment


if __name__ == "__main__":

    env = Enviroment(task_name="bridge", io="highlvl", use_images=False)
    messages = env.get_messages()
    print(messages[0]["content"][0]["text"])
    