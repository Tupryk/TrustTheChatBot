import robotic as ry


def BridgeScene() -> tuple[ry.Config, list[str], str]:
    C = ry.Config()
    C.addFile(ry.raiPath('../rai-robotModels/scenarios/pandaSingle.g'))

    C.delFrame("panda_collCameraWrist")
    C.getFrame("table").setShape(ry.ST.ssBox, size=[1., 1., .1, .02])

    names = ["red", "green", "blue"]

    # Objects
    for i in range(3):
        color = [0., 0., 0.]
        color[i%3] = 1.
        C.addFrame(f"block_{names[i]}") \
            .setPosition([(i%3)*.15, (i//3)*.1+.1, .71]) \
            .setShape(ry.ST.ssBox, size=[.04, .04, .12, 0.005]) \
            .setColor(color) \
            .setContact(1) \
            .setMass(.1)
        
    relevant_frame_names = [line for line in C.getFrameNames()
                            if not line.startswith("l_") and
                            not line.startswith("small_") and
                            not line.startswith("shelf_") and
                            not line.startswith("big_")]
    
    camera_frame = "cameraTop"
    return C, relevant_frame_names, camera_frame
