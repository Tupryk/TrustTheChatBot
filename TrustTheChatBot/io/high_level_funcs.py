import time
import numpy as np
import robotic as ry
from TrustTheChatBot.simulator import Simulator
import TrustTheChatBot.Robotic_Manipulation.manipulation as manip


class RAIVec:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class RAIObj:
    def __init__(self, C: ry.Config, name: str):
        self.C = C
        self.name = name

    @property
    def pos(self) -> RAIVec:
        nums = self.C.getFrame(self.name).getPosition()
        vec = RAIVec(*nums)
        return vec
    
    @property
    def size(self) -> RAIVec:
        real_size = self.C.getFrame(self.name).getSize()[:3]

        # rel_size = RAIVec(0, 0, 0)
        # # Height
        # rel_size.z = np.argmax([
        #     np.abs(self.C.eval(ry.FS.scalarProductXZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductYZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductZZ, [self.name, "table"])[0][0])
        #     ])
        # # Height
        # rel_size.z = np.argmax([
        #     np.abs(self.C.eval(ry.FS.scalarProductXZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductYZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductZZ, [self.name, "table"])[0][0])
        #     ])
        # # Height
        # rel_size.z = np.argmax([
        #     np.abs(self.C.eval(ry.FS.scalarProductXZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductYZ, [self.name, "table"])[0][0]),
        #     np.abs(self.C.eval(ry.FS.scalarProductZZ, [self.name, "table"])[0][0])
        #     ])
        if len(real_size) == 2:
            real_size = [real_size[1]*2, real_size[1]*2, real_size[0]]
        return RAIVec(*real_size)


class RobotEnviroment:
    def __init__(self,
                 C: ry.Config,
                 visuals: bool=False,
                 verbose: int=0,
                 compute_collisions: bool=True,
                 on_real: bool=False,
                 use_botop: bool=False,
                 use_sim: bool=True):
        self.C = C
        if on_real:
            self.bot = ry.BotOp(self.C, on_real)
            self.bot.home(self.C)
        self.visuals = visuals
        self.verbose = verbose
        self.grabbed_frame = ""
        self.grasp_direction = ""
        self.path = np.array([])
        self.compute_collisions = compute_collisions
        self.use_botop = use_botop
        if use_botop:
            self.bot = ry.BotOp(C, False)
        self.use_sim = use_sim
        self.feasible = True
        self.i = 0

    def pick(self, frame: str) -> bool:

        if not self.feasible:
            return self.feasible
        
        assert self.grabbed_frame == ""

        graspDirections = ['x', 'y']
        gripper = "l_gripper"
        palm = "l_palm"

        for gd in graspDirections:

            M = manip.ManipulationModelling()
            M.setup_sequence(self.C, 1, accumulated_collisions=self.compute_collisions)
            M.grasp_box(1., gripper, frame, palm, gd)
            M.solve(verbose=self.verbose)
            if not M.feasible:
                continue

            M2 = M.sub_motion(0, accumulated_collisions=self.compute_collisions)
            M2.no_collisions([.3,.7], [palm, frame], margin=.05)
            M2.retract([.0, .2], gripper)
            M2.approach([.8, 1.], gripper)
            self.path = M2.solve(verbose=self.verbose)
            if not M2.feasible:
                continue

            self.i += 1
            if self.visuals:
                M2.play(self.C)
                self.C.attach(gripper, frame)
            
            elif self.use_botop:

                self.bot.sync(self.C, .1)
                self.bot.move(self.path, [3.])
                while self.bot.getTimeToEnd() > 0:
                    self.bot.sync(self.C, .1)
                self.bot.gripperClose(ry._left)
                while not self.bot.gripperDone(ry._left):
                    self.bot.sync(self.C)
                self.C.attach(gripper, frame)

            elif self.use_sim:
                C2 = ry.Config()
                C2.addConfigurationCopy(self.C)
                sim = Simulator(C2)
                xs, qs, xdots, qdots = sim.run_trajectory(self.path, 2, real_time=False)

                sim._sim.closeGripper("l_gripper")
                self.C.setJointState(qs[-1])
                
                self.C.attach(gripper, frame)

            else:
                qt = self.path[-1]
                self.C.setJointState(qt)
                self.C.attach(gripper, frame)

            self.grabbed_frame = frame
            self.grasp_direction = gd
            return True
    
        self.feasible = False
        return False


    def place_simple(self, x: float, y: float, z: float=.0, rotated: bool=False, yaw: float=None) -> bool:
        if not self.feasible:
            return False
        
        assert self.grabbed_frame != ""

        table = "table"
        palm = "l_palm"
        table_frame = self.C.getFrame("table")
        
        if rotated and self.grasp_direction == 'x':
            place_direction = ['y', 'yNeg']
        elif rotated and self.grasp_direction == 'y':
            place_direction = ['x', 'xNeg']
        elif not rotated:
            place_direction = ['z', 'zNeg']

        feasible = False
        Ms = []
        for i, direction in enumerate(place_direction):
            M = manip.ManipulationModelling()
            M.setup_sequence(self.C, 1, accumulated_collisions=self.compute_collisions, homing_scale=.1)
            
            if not z:
                M.place_box(1., self.grabbed_frame, table, palm, direction)
                M.target_relative_xy_position(1., self.grabbed_frame, table, [x, y])
            else:
                table_offset = table_frame.getPosition()[2] + table_frame.getSize()[2]*.5
                if z < table_offset:
                    z += table_offset
                M.place_box(1., self.grabbed_frame, table, palm, direction, on_table=False)
                M.target_position(1., self.grabbed_frame, [x, y, z])

            if yaw != None:

                if direction == "x" or direction == "xNeg":
                    feature = ry.FS.scalarProductXZ
                elif direction == "y" or direction == "yNeg":
                    feature = ry.FS.scalarProductXX
                elif direction == "z" or direction == "zNeg":
                    feature = ry.FS.scalarProductXX
                else:
                    raise Exception(f"'{place_direction}' is not a valid up vector for a place motion!")
                
                M.komo.addObjective([.8, 1.], feature, [table, self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(yaw)])

            M.solve(verbose=self.verbose)
            Ms.append((M, M.ret.sos + M.ret.eq))
            if M.feasible:    
                feasible = True

        Ms.sort(key=lambda x: x[1])  # Sort by cost (index 1)
        if not feasible:    
            self.feasible = False
            return False

        M = Ms[0][0]

        M3 = M.sub_motion(0, accumulated_collisions=self.compute_collisions)
        self.path = M3.solve(verbose=self.verbose)
        if not M3.ret.feasible:
            # M3.komo.report(plotOverTime=True)
            # self.C.view(False)
            self.feasible = False
            return False

        self.i += 1
        if self.visuals:
            M3.play(self.C)
            self.C.attach(table, self.grabbed_frame)
        
        elif self.use_botop:
            self.bot.move(self.path, [3.])
            while self.bot.getTimeToEnd() > 0:
                self.bot.sync(self.C)
            self.bot.gripperMove(ry._left)
            while not self.bot.gripperDone(ry._left):
                self.bot.sync(self.C)
            self.C.attach(table, self.grabbed_frame)

        elif self.use_sim:
            self.C.attach(table, self.grabbed_frame)

            C2 = ry.Config()
            C2.addConfigurationCopy(self.C)
            sim = Simulator(C2)
            xs, qs, xdots, qdots = sim.run_trajectory(self.path, 2, real_time=False, close_gripper=True)
            
            self.C.setJointState(qs[-1])
            self.C.setFrameState(xs[-1])
        
        else:
            qt = self.path[-1]
            self.C.setJointState(qt)
            self.C.attach(table, self.grabbed_frame)

        self.grabbed_frame = ""
        self.grasp_direction = ""
        return True


    def place(self, x: float, y: float, z: float=.0, roll: float=None, pitch: float=None, yaw: float=None) -> bool:
        if not self.feasible:
            return False
        
        assert self.grabbed_frame != ""

        table = "table"
        palm = "l_palm"
        table_frame = self.C.getFrame("table")

        if roll == None and pitch == None and yaw == None:
            place_direction = 'z'
        else:
            place_direction = None

        self.feasible = False
        Ms = []
        M = manip.ManipulationModelling()
        M.setup_sequence(self.C, 1, accumulated_collisions=self.compute_collisions, homing_scale=.1)
        
        if not z:
            M.place_box(1., self.grabbed_frame, table, palm, place_direction)
            M.target_relative_xy_position(1., self.grabbed_frame, table, [x, y])
        else:
            table_offset = table_frame.getPosition()[2] + table_frame.getSize()[2]*.5
            if z < table_offset:
                z += table_offset
            M.place_box(1., self.grabbed_frame, table, palm, place_direction, on_table=False)
            M.target_position(1., self.grabbed_frame, [x, y, z])

        if roll != None:
            M.komo.addObjective([.8, 1.], ry.FS.scalarProductYY, [table, self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(roll)])
            if pitch == None and yaw == None:
                M.komo.addObjective([.8, 1.], ry.FS.vectorX, [self.grabbed_frame], ry.OT.eq, [1e1], [1., 0., 0.])
        if pitch != None:
            M.komo.addObjective([.8, 1.], ry.FS.scalarProductZZ, [table, self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(pitch)])
            if roll == None and yaw == None:
                M.komo.addObjective([.8, 1.], ry.FS.vectorY, [self.grabbed_frame], ry.OT.eq, [1e1], [0., 1., 0.])
        if yaw != None:
            M.komo.addObjective([.8, 1.], ry.FS.scalarProductXX, [table, self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(yaw)])
            if roll == None and pitch == None:
                M.komo.addObjective([.8, 1.], ry.FS.vectorZ, [self.grabbed_frame], ry.OT.eq, [1e1], [0., 0., 1.])

        M.solve(verbose=self.verbose)
        Ms.append((M, M.ret.sos + M.ret.eq))
        if M.feasible:    
            self.feasible = True

        Ms.sort(key=lambda x: x[1])  # Sort by cost (index 1)
        if not self.feasible:    
            self.feasible = False
            return False

        M = Ms[0][0]

        M3 = M.sub_motion(0, accumulated_collisions=self.compute_collisions)
        self.path = M3.solve(verbose=self.verbose)
        if not M3.ret.feasible:
            # M3.komo.report(plotOverTime=True)
            # self.C.view(False)
            self.feasible = False
            return False

        self.i += 1
        if self.visuals:
            M3.play(self.C)
            self.C.attach(table, self.grabbed_frame)
        
        elif self.use_botop:
            self.bot.move(self.path, [3.])
            while self.bot.getTimeToEnd() > 0:
                self.bot.sync(self.C)
            self.bot.gripperMove(ry._left)
            while not self.bot.gripperDone(ry._left):
                self.bot.sync(self.C)
            self.C.attach(table, self.grabbed_frame)

        elif self.use_sim:
            self.C.attach(table, self.grabbed_frame)

            C2 = ry.Config()
            C2.addConfigurationCopy(self.C)
            sim = Simulator(C2)
            xs, qs, xdots, qdots = sim.run_trajectory(self.path, 2, real_time=False, close_gripper=True)
            
            self.C.setJointState(qs[-1])
            self.C.setFrameState(xs[-1])
        
        else:
            qt = self.path[-1]
            self.C.setJointState(qt)
            self.C.attach(table, self.grabbed_frame)

        self.grabbed_frame = ""
        self.grasp_direction = ""
        return True
    

    def set_grabbed_frame_pose(self,
              x: float=None,
              y: float=None,
              z: float=None,
              roll: float=None,
              pitch: float=None,
              yaw: float=None) -> bool:
        
        if not self.feasible:
            return False
        
        assert self.grabbed_frame != ""

        table_frame = self.C.getFrame("table")

        komo = ry.KOMO(self.C, 1, 32, 2, self.compute_collisions)
        komo.addControlObjective([], 0, 1e-2)
        komo.addControlObjective([], 1, 1e-1)
        komo.addControlObjective([], 2, 1e-1)
        komo.addObjective([], ry.FS.jointLimits, [], ry.OT.ineq, [1e0])
        if self.compute_collisions:
            komo.addObjective([], ry.FS.accumulatedCollisions, [], ry.OT.eq, [1e0])

        if x != None:
            komo.addObjective([1.], ry.FS.position, [self.grabbed_frame], ry.OT.eq, [1e1, 0, 0], [x, 0., 0.])
        if y != None:
            komo.addObjective([1.], ry.FS.position, [self.grabbed_frame], ry.OT.eq, [0, 1e1, 0], [0., y, 0.])
        if z != None:
            table_offset = table_frame.getPosition()[2] + table_frame.getSize()[2]*.5
            if z < table_offset:
                z += table_offset
            komo.addObjective([1.], ry.FS.position, [self.grabbed_frame], ry.OT.eq, [0, 0, 1e1], [0., 0., z])
        
        if roll != None:
            komo.addObjective([.8, 1.], ry.FS.scalarProductYY, ["table", self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(roll)])
            if pitch == None and yaw == None:
                komo.addObjective([.8, 1.], ry.FS.vectorX, [self.grabbed_frame], ry.OT.eq, [1e1], [1., 0., 0.])
        if pitch != None:
            komo.addObjective([.8, 1.], ry.FS.scalarProductZZ, ["table", self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(pitch)])
            if roll == None and yaw == None:
                komo.addObjective([.8, 1.], ry.FS.vectorY, [self.grabbed_frame], ry.OT.eq, [1e1], [0., 1., 0.])
        if yaw != None:
            komo.addObjective([.8, 1.], ry.FS.scalarProductXX, ["table", self.grabbed_frame], ry.OT.eq, [1e1], [np.cos(yaw)])
            if roll == None and pitch == None:
                komo.addObjective([.8, 1.], ry.FS.vectorZ, [self.grabbed_frame], ry.OT.eq, [1e1], [0., 0., 1.])

        sol = ry.NLP_Solver()
        sol.setProblem(komo.nlp())
        sol.setOptions(damping=1e-1, verbose=self.verbose-1, stopTolerance=1e-3, maxLambda=100., stopInners=20, stopEvals=200)
        ret = sol.solve()
        if not ret.feasible:
            self.feasible = False
            return False

        self.path = komo.getPath()

        self.i += 1
        if self.visuals:
            for t in range(self.path.shape[0]):
                self.C.setJointState(self.path[t])
                self.C.view(False)
                time.sleep(1/self.path.shape[0])
        
        elif self.use_botop:
            self.bot.move(self.path, [3.])
            while self.bot.getTimeToEnd() > 0:
                self.bot.sync(self.C)

        elif self.use_sim:

            C2 = ry.Config()
            C2.addConfigurationCopy(self.C)
            sim = Simulator(C2)
            xs, qs, xdots, qdots = sim.run_trajectory(self.path, 2, real_time=False, close_gripper=True)
            
            self.C.setJointState(qs[-1])
            self.C.setFrameState(xs[-1])
        
        else:
            qt = self.path[-1]
            self.C.setJointState(qt)

        return True


    def push(self, frame: str, relative_x: float, relative_y: float) -> bool:

        obj_pos = self.C.getFrame(frame).getPosition()
        target_pos = obj_pos + np.array([relative_x, relative_y, 0.])
        
        gripper = "l_gripper"
        table = "table"
        
        M = manip.ManipulationModelling()
        M.setup_pick_and_place_waypoints(self.C, gripper, frame, 1e-1, accumulated_collisions=False)
        pushStart = M.straight_push([1.,2.], frame, gripper, table)
        M.target_xy_position(2., frame, target_pos)
        M.solve(verbose=self.verbose)
        if not M.ret.feasible:
            self.feasible = False
            return False

        M1 = M.sub_motion(0, accumulated_collisions=False)
        M1.retractPush([.0, .15], gripper, .03)
        M1.approachPush([.85, 1.], gripper, .03)
        M1.no_collisions([.15,.85], [frame, 'l_finger1'], .02)
        M1.no_collisions([.15,.85], [frame, 'l_finger2'], .02)
        M1.no_collisions([.15,.85], [frame, 'l_palm'], .02)
        M1.no_collisions([], [table, 'l_finger1'], .0)
        M1.no_collisions([], [table, 'l_finger2'], .0)
        path1 = M1.solve(verbose=self.verbose)
        if not M1.ret.feasible:
            self.feasible = False
            return False

        M2 = M.sub_motion(1, accumulated_collisions=False)
        M2.komo.addObjective([], ry.FS.positionRel, [gripper, pushStart], ry.OT.eq, 1e1*np.array([[1,0,0],[0,0,1]]))
        path2 = M2.solve(verbose=self.verbose)
        if not M2.ret.feasible:
            self.feasible = False
            return False

        if self.visuals:
            M1.play(self.C, 1.)
            self.C.attach(gripper, frame)
            M2.play(self.C, 1.)
            self.C.attach(table, frame)
        
        elif self.use_sim:
            #TODO
            pass

        else:
            self.bot.move(path1, [3.])
            while self.bot.getTimeToEnd() > 0:
                self.bot.sync(self.C)
            self.bot.move(path2, [3.])
            while self.bot.getTimeToEnd() > 0:
                self.bot.sync(self.C)

        self.path = np.concatenate((path1, path2))

        return True
    

    def getObj(self, object_name: str) -> RAIObj:
        obj = RAIObj(self.C, object_name)
        return obj
