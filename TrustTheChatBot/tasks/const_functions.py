import numpy as np
import robotic as ry


def bridge_cost_func(C: ry.Config, verbose: int=0):
    
    red_block = C.getFrame("block_red")
    green_block = C.getFrame("block_green")
    blue_block = C.getFrame("block_blue")

    red_block_error = 0
    green_block_error = 0
    blue_block_error = 0

    # Positions
    green_block_error += np.abs(np.linalg.norm(green_block.getPosition() - red_block.getPosition()) - 0.12)
    blue_block_error += np.abs((blue_block.getPosition()[2] - red_block.getPosition()[2]) - .06 - .02)

    # Rotations
    blue_block_error += np.abs(C.eval(ry.FS.scalarProductZZ, ["block_blue", "table"])[0][0])
    total_cost = red_block_error + green_block_error + blue_block_error

    if verbose:
        print("+-------------------------------+")
        print("Red block error: ", red_block_error)
        print("Green block error: ", green_block_error)
        print("Blue block error: ", blue_block_error)
        print("Total cost: ", total_cost)
        print("+-------------------------------+")

    return total_cost


def romani_cost_func(C: ry.Config, verbose: int=0):

    block_red = C.getFrame("block_red")
    block_green = C.getFrame("block_green")
    block_blue = C.getFrame("block_blue")

    block_red_error = 0
    block_green_error = 0
    block_blue_error = 0

    block_red_err_alignment = np.abs(np.round(C.eval(ry.FS.scalarProductZZ, ["block_red", "table"])[0][0], 1))
    block_green_err_alignment = np.abs(np.round(C.eval(ry.FS.scalarProductXZ, ["block_green", "table"])[0][0], 1))
    block_blue_err_alignment = np.abs(np.round(C.eval(ry.FS.scalarProductZZ, ["block_blue", "table"])[0][0], 1))
    
    block_green_err_height = 10*np.abs(block_green.getPosition()[2]-block_red.getPosition()[2]-.08) 

    block_blue_err_height = 10*np.abs(block_blue.getPosition()[2]-block_green.getPosition()[2]-.08) 

    block_green_err_alignment = np.abs(C.eval(ry.FS.scalarProductZZ, ["block_red", "block_green"])[0][0])
    block_blue_err_alignment = np.abs(C.eval(ry.FS.scalarProductZZ, ["block_red", "block_blue"])[0][0])

    block_red_error += block_red_err_alignment
    block_green_error += block_green_err_alignment + block_green_err_height #+ block_green_err_alignment
    block_blue_error += block_blue_err_alignment + block_blue_err_height #+ block_blue_err_alignment

    total_cost = block_red_error + block_green_error + block_blue_error  

    if verbose:
        print("+-------------------------------+")
        print("Block 0/2 error alignment:", block_blue_err_alignment)

        print("Block red error alignment:", block_red_err_alignment)
        print("Block green error alignment:", block_green_err_alignment)
        print("Block blue error alignment:", block_blue_err_alignment)

        print("Total cost: ", total_cost)
        print(np.abs(block_green.getPosition()[2]-block_red.getPosition()[2]) )
        print("+-------------------------------+")

    return total_cost


def beer_cost_func(C: ry.Config, verbose: int=0):

    beer = C.getFrame("beer")
    glass = C.getFrame("glass")

    beer_err_rot = np.abs(C.eval(ry.FS.scalarProductYY, ["table", "beer"])[0][0] - 1.)
    glass_err_rot = 0
    
    a = glass.getPosition() + np.array([-0.03, 0.04, 0.05 + 0.12])
    b = beer.getPosition()
    beer_err_pos = np.linalg.norm(a-b)
    glass_err_pos = 0

    beer_error = beer_err_pos + beer_err_rot
    glass_error = glass_err_pos + glass_err_rot

    total_cost = beer_error + glass_error

    if verbose:
        print("+-------------------------------+")
        print("Beer error rotation:", beer_err_rot)
        print("Beer error position:", beer_err_pos)
        print("Total cost: ", total_cost)
        print("+-------------------------------+")

    return total_cost
