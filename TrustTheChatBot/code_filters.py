
def cleanup_komo(original_func: str) -> str:
    new_func = original_func
    return new_func


def cleanup_manip(original_func: str) -> str:
    new_func = original_func
    return new_func


def cleanup_highlvl_func(original_func: str, compute_collisions: bool=True, visuals: bool=False) -> str:

    high_funcs = ["pick", "place", "push", "getObj"]

    lines = original_func.split('\n')

    # Create the interface with the robot
    new_line = f"    env = RobotEnviroment(C, visuals={visuals}, verbose=0, compute_collisions={compute_collisions})"
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            insert_index = i + 1
            break
    lines.insert(insert_index, new_line)

    # Execute the function if it is not yet being executed in the code
    if lines[-1].startswith(" "*4) or lines[-1].startswith("\t") or lines[-1] == "":
        execute_command = lines[insert_index-1].replace("def ", "").replace(":", "")
        lines.append(execute_command)

    new_func = '\n'.join(lines)

    # Rewrite the high lvl function calls as methods of the robot enviroment
    for f in high_funcs:
        new_func = new_func.replace(f"{f}(", f"env.{f}(")
    
    return new_func
