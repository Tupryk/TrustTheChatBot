import os
import re
import time
import robotic as ry
import matplotlib.pyplot as plt


def load_txt(file_path: str):
    with open(file_path, 'r') as file:
        text = file.read()
    return text\


def build_message(role: str, text: str, image_path: str="") -> dict:
    message = {
        "role": role,
        "content": [],
    }
    if text:
        message["content"].append({
            "type": "text",
            "text": text,
        })
    if image_path:
        message["content"].append({
            "type": "image",
            "image": image_path,
        })
    return message


def take_picture(C: ry.Config, camera_frame_name: str, im_idx: int):

    folder_path = "./scene_images"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    camera_frame = C.getFrame(camera_frame_name)
    C.view_setCamera(camera_frame)
    C.view()
    time.sleep(1.)

    rgb = C.view_getRgb()

    image_path = f"{folder_path}/im{im_idx}.jpg"
    plt.imsave(image_path, rgb)


def extract_code_block(text):
    match = re.search(r"```(?:python\s*)?(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text
