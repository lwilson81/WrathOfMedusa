import time
import numpy as np
from xarm import XArmAPI
from queue import Queue
from threading import Thread
from trajectoryGen import fifth_poly


# Prepare Robots
def setup():
    for i in range(len(arms)):
        arms[i].set_simulation_robot(on_off=False)
        # a.motion_enable(enable=True)
        arms[i].clean_warn()
        arms[i].clean_error()
        arms[i].set_mode(0)
        arms[i].set_state(0)
        arms[i].set_servo_angle(angle=IP[i], wait=False,
                                speed=10, acceleration=0.25, is_radian=False)
    print("Ready to start.")


# Start Positions (not Live mode)
def moveToStart(index):
    print(index)
    arms[index].set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)


def moveToStrumPos(index):
    arms[index].set_servo_angle(angle=IP[index], wait=True, speed=0.4, acceleration=0.25,
                                is_radian=True)


# Strum Commands
def strumbot(numarm, traj):
    pos = IP[numarm]
    j_angles = pos
    track_time = time.time()
    initial_time = time.time()
    for i in range(len(traj)):
        # run command
        j_angles[4] = traj[i]
        arms[numarm].set_servo_angle_j(angles=j_angles, is_radian=False)

        while track_time < initial_time + 0.004:
            track_time = time.time()
            time.sleep(0.0001)
        initial_time += 0.004


def strummer(queue, robotNum):
    i = 0
    upStrumTraj = fifth_poly(-strumD / 2, strumD / 2, speed)
    downStrumTraj = fifth_poly(strumD/2, -strumD/2, speed)
    strumTrajectories = [upStrumTraj, downStrumTraj]

    while True:
        queue.get()
        arms[i].set_mode(1)
        arms[i].set_state(1)
        print("Strum Command Recieved for Robot " + str(robotNum))

        strumDirection = i % 2
        time.sleep(delayarray[strumDirection, robotNum])
        strumbot(robotNum, strumTrajectories[strumDirection])

        i += 1


def playPattern():
    q0.put(0)
    # q1.put(1)
    # q2.put(2)
    # q3.put(3)
    # q4.put(4)


# Accessors
def getArms(): return arms
def getIPs(): return IP


# Robot Initialization Stuff
global IP
global arms
global strumD
global speed
global notes

ROBOT = "xArms"
PORT = 5003

strumD = 30
speed = 0.25

# Initial Robot Strumming Positions
IP0 = [-1, 87.1, -2, 126.5, -strumD/2, 51.7, -45]
IP1 = [2.1, 86.3, 0, 127.1, -strumD/2, 50.1, -45]
IP2 = [1.5, 81.6, 0.0, 120, -strumD/2, 54.2, -45]
IP3 = [2.5, 81, 0, 117.7, -strumD/2, 50.5, -45]
IP4 = [-1.6, 81.8, 0, 120, -strumD/2, 50.65, -45]
IP = [IP0, IP1, IP2, IP3, IP4]

arm0 = XArmAPI('192.168.1.208')
arm1 = XArmAPI('192.168.1.226')
arm2 = XArmAPI('192.168.1.244')
arm3 = XArmAPI('192.168.1.203')
arm4 = XArmAPI('192.168.1.237')
arms = [arm0, arm1, arm2, arm3, arm4]

# Initialize
q0 = Queue()
q1 = Queue()
q2 = Queue()
q3 = Queue()
q4 = Queue()
qList = [q0, q1, q2, q3, q4]

xArm0 = Thread(target=strummer, args=(q0, 0,))  # num 2
xArm1 = Thread(target=strummer, args=(q1, 1,))  # num 4
xArm2 = Thread(target=strummer, args=(q2, 2,))  # num 1
xArm3 = Thread(target=strummer, args=(q3, 3,))  # num 3
xArm4 = Thread(target=strummer, args=(q4, 4,))  # num 5

# Time delay before playing
delayarray = np.array([[0.15, 0.15, 0.15, 0.15, 0.15, 0.0, 0.0], [
                      0.1, 0.15, 0.1, 0.15, 0.125, 0.0, 0.0]])
