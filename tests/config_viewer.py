import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TrustTheChatBot.tasks.configurations import BeerScene


if __name__ == "__main__":

    C, frame_names, camera_frame = BeerScene()
    print("Frame names: ", frame_names)
    print("Camera Frame: ", camera_frame)
    C.view(True)
    