import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from TrustTheChatBot.tasks.configurations import BridgeScene
from TrustTheChatBot.high_level_funcs import RobotEnviroment


if __name__ == "__main__":

    C, _, _ = BridgeScene()

    env = RobotEnviroment(C, visuals=True, verbose=1, compute_collisions=False)

    env.pick("block_red")

    x = np.random.uniform(-.1, .1) - .105
    y = np.random.uniform(-.1, .1) + .4
    env.place(x, y)

    relative_x = np.random.uniform(-.05, .05) - .105
    relative_y = np.random.uniform(-.05, .05) + .4
    env.push("block_red", relative_x, relative_y)
