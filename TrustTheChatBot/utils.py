import os
import re
import ast
import time
import numpy as np
import robotic as ry
import matplotlib.pyplot as plt


def str_to_np_array(text: str) -> np.ndarray:
    return np.array(ast.literal_eval(text), dtype=np.float32)


def load_txt(file_path: str):
    with open(file_path, 'r') as file:
        text = file.read()
    return text\


def build_message(role: str, text: str, image_path: str="") -> dict:
    message = {
        "role": role,
        "content": [],  # TODO: investigate whether this list format is really suitable for out purposes
    }
    if text:
        message["content"].append({
            "type": "text",
            "text": text,
        })
    if len(image_path) > 0:
        message["content"].append({
            "type": "image",
            "image": image_path,
        })
    return message


def take_picture(C: ry.Config, camera_frame_name: str, im_idx: int) -> str:

    folder_path = "./scene_images"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    camera_frame = C.getFrame(camera_frame_name)
    C.view()
    C.view_setCamera(camera_frame)
    time.sleep(1.)
    C.view()

    rgb = C.view_getRgb()

    image_path = f"{folder_path}/im{im_idx}.jpg"
    plt.imsave(image_path, rgb)

    return image_path


def extract_code_block(text):
    match = re.search(r"```(?:python\s*)?(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text


def add_default_cam(C: ry.Config, frame_name: str="cameraFront") -> str:
    pos = np.array([1.93710244, 3.87420489, 1.38742049])
    rot = np.array([-0.15505454, 0.16954202, 0.71819151, -0.65682155])
    C.addFrame(frame_name) \
        .setShape(ry.ST.marker, [.1]) \
        .setPosition(pos) \
        .setQuaternion(rot)
    return frame_name
