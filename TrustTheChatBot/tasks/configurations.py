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
        
    relevant_frame_names = [f for f in C.getFrameNames()
                            if not f.startswith("l_") and
                            not f.startswith("small_") and
                            not f.startswith("shelf_") and
                            not f.startswith("big_")]
    
    camera_frame = "cameraTop"
    return C, relevant_frame_names, camera_frame


def BeerScene() -> tuple[ry.Config, list[str], str]:
    C = ry.Config()
    C.addFile(ry.raiPath('../rai-robotModels/scenarios/pandaSingle.g'))

    C.delFrame("panda_collCameraWrist")
    C.getFrame("table").setShape(ry.ST.ssBox, size=[1., 1., .1, .02])
    
    # C.addFrame("beer") \
    #     .setShape(ry.ST.cylinder, [.19, .036]) \
    #     .setPosition([-.1, 0., .75]) \
    #     .setColor([1., 1., .3]) \
    #     .setContact(1) \
    #     .setMass(.1)
    
    C.addFrame("beer") \
        .setShape(ry.ST.ssBox, [.072, .072, .19, .05]) \
        .setPosition([-.1, 0., .75]) \
        .setColor([1., 1., .3]) \
        .setContact(1) \
        .setMass(.1)
    
    C.addFrame("glass") \
        .setShape(ry.ST.cylinder, [.12, .045]) \
        .setPosition([.1, .2, .75-.03]) \
        .setColor([1., 1., 1., .7]) \
        .setContact(1) \
        .setMass(.1)
        
    relevant_frame_names = [f for f in C.getFrameNames()
                            if not f.startswith("l_")]
    
    camera_frame = "cameraTop"
    return C, relevant_frame_names, camera_frame
