import ast
import os
import re
import json
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
REPO_PATH = Path(os.environ["REPO_PATH"])


def extract_json_between_markers(llm_output):
    # Regular expression pattern to find JSON content between ```json and ```
    json_pattern = r"```json(.*?)```"
    matches = re.findall(json_pattern, llm_output, re.DOTALL)

    if not matches or len(matches) == 0:
        # Fallback: Try to find any JSON-like content in the output
        json_pattern = r"({.*})"
        matches = re.findall(json_pattern, llm_output, re.DOTALL)

    for json_string in matches:
        json_string = json_string.strip()
        try:
            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError as e:
            print(e)
            # Attempt to fix common JSON issues
            try:
                print(e)
                pattern = r'("code":\s*")([\s\S]*?)(")'

                def replacer(match):
                    code_content = match.group(2)
                    escaped_content = code_content.replace("\n", "\\n")
                    return match.group(1) + escaped_content + match.group(3)

                fixed_text = re.sub(pattern, replacer, json_string, flags=re.DOTALL)
                fixed_text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", fixed_text)
                parsed_json = json.loads(fixed_text)
                return parsed_json
            except json.JSONDecodeError as e:
                print(e)
                try:
                    # Remove invalid control characters
                    json_string_clean = re.sub(r"[\x00-\x1F\x7F]", "", json_string)
                    parsed_json = json.loads(json_string_clean)
                    return parsed_json
                except json.JSONDecodeError as e:
                    continue

    return None  # No valid JSON found


def cleanup_komo(original_func: str) -> str:
    json_output = extract_json_between_markers(original_func)
    assert json_output is not None, "Failed to extract JSON from LLM output"
    n_phases = int(json_output.get("n_phases", 1))
    komo_content = json_output.get("code")
    with open(REPO_PATH / "TrustTheChatBot" / "prompts" / "io" / "komo" / "komo_setup.txt", "r") as f:
        komo_prefix = f.read()
    new_func =  f"n_phases = {n_phases}\n" + komo_prefix + komo_content

    return new_func


def cleanup_manip(original_func: str) -> str:
    new_func = original_func
    return new_func


def cleanup_highlvl_func(original_func: str, compute_collisions: bool=True, visuals: bool=False) -> str:

    high_funcs = ["pick", "place", "push", "getObj", "place_simple", "set_grabbed_frame_pose"]

    lines = original_func.split('\n')

    # Create the interface with the robot
    new_line = f"    env = RobotEnviroment(C, visuals={visuals}, verbose=0, compute_collisions={compute_collisions})"
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            insert_index = i + 1
            break
    lines.insert(insert_index, new_line)

    # Execute the function if it is not yet being executed in the code
    if lines[-1].startswith(" ") or lines[-1].startswith("\t") or lines[-1] == "":
        execute_command = lines[insert_index-1].replace("def ", "").replace(":", "")
        lines.append(execute_command)

    for i, l in enumerate(lines):
        if "rotated" in l and "place" in l:
           lines[i] = l.replace("place", "place_simple") 

    new_func = '\n'.join(lines)

    # Rewrite the high lvl function calls as methods of the robot enviroment
    for f in high_funcs:
        new_func = new_func.replace(f"{f}(", f"env.{f}(")
    
    return new_func
