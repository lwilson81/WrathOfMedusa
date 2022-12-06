import time
import numpy as np
import random

from helpers import chordDegreeToModifier
from xarm import XArmAPI
from queue import Queue
from threading import Thread
from trajectoryGen import fifth_poly, spline_poly


# Prepare Robots
def setup():
    for i in range(len(arms)):
        arms[i].set_simulation_robot(on_off=False)
        arms[i].motion_enable(enable=True)
        arms[i].clean_warn()
        arms[i].clean_error()
        arms[i].set_mode(0)
        arms[i].set_state(0)
        arms[i].set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)
    print("Ready to start.")


# Start Positions (not Live mode)
def moveToStart(index):
    arms[index].set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)


def moveToStrumPos(index):
    arms[index].set_servo_angle(angle=IP[index], wait=False,
                                speed=20, acceleration=0.25, is_radian=False)


def turnOffLive():
    for i in range(len(arms)):
        arms[i].set_mode(0)
        arms[i].set_state(0)
        moveToStart(i)

    waitForRobots()


def turnOnLive():
    for i in range(len(arms)):
        moveToStrumPos(i)

    waitForRobots()

    for i in range(len(arms)):
        arms[i].set_mode(1)
        arms[i].set_state(0)


def waitForRobots():
    not_safe_to_continue = True
    while not_safe_to_continue:
        not_safe_to_continue = False
        for arm in arms:
            if arm.get_is_moving():
                not_safe_to_continue = True


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
    downStrumTraj = fifth_poly(strumD / 2, -strumD / 2, speed)
    strumTrajectories = [upStrumTraj, downStrumTraj]

    while True:
        variation = queue.get()
        print("Strum Command Recieved for Robot " + str(robotNum))

        strumDirection = i % 2

        time.sleep(delayArray[variation][strumDirection, robotNum])
        strumbot(robotNum, strumTrajectories[strumDirection])

        i += 1


def drumbot(trajz, trajp, arm):
    track_time = time.time()
    initial_time = time.time()
    for i in range(len(trajz)):
        mvpose = [492, 0, trajz[i], 180, trajp[i], 0]
        drums[0].set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        while track_time < initial_time + 0.004:
            track_time = time.time()
            time.sleep(0.0001)
        initial_time += 0.004


def drummer(inq, num):
    trajz = spline_poly(325, 35, .08, .08, 0.01)
    trajp = spline_poly(-89, -28, .08, .08, 0.01)

    trajz2 = spline_poly(325, 35, .08, .08, .1)
    trajp2 = spline_poly(-89, -28, .08, .08, .1)

    trajz3 = spline_poly(325, 35, .08, .08, .15)
    trajp3 = spline_poly(-89, -28, .08, .08, .15)

    i = 0
    while True:
        i += 1
        play = inq.get()

        # end of run indef
        if i % 3 == 1:
            drumbot(trajz, trajp, num)

        elif i % 3 == 2:
            drumbot(trajz2, trajp2, num)

        elif i % 3 == 0:
            drumbot(trajz3, trajp3, num)


def rotateRandomly(chordDegree):
    for i in range(len(arms)):
        home = [0.0, 0.0, 0.0, 1.57, 0.0, 0.0, 0.0]

        modifier = chordDegreeToModifier(chordDegree)

        # TODO: replace with numpy and broadcasting for optimization
        for j in range(7):
            home[j] += modifier * (random.random() - 0.5)

        arms[i].set_servo_angle(angle=home, wait=False, speed=0.4,
                                acceleration=0.25, is_radian=True)


def playPattern(chord):
    # TODO: Use dictionary instead
    if 'C7' in chord:
        print("Special C recognized")
        loadQueues([1, 3, 4], 'C')

    elif 'C' in chord:
        print("C recognized")
        loadQueues([1, 3, 4], 'C')

    elif 'F' in chord:
        print("F recognized")
        loadQueues([1, 2, 3], 'F')

    elif 'G' in chord:
        print("G recognized")
        loadQueues([2, 3, 4], 'G')

    elif 'D' in chord:
        drumQ.put(0)



def loadQueues(indexes, value):
    for i in indexes:
        qList[i].put(value)


# Accessors
def getArms(): return arms


def getIPs(): return IP


# Robot Initialization Stuff
global IP
global arms
global drums
global strumD
global speed
global notes

ROBOT = "xArms"
PORT = 5003

strumD = 30
speed = 0.25

# Initial Robot Strumming Positions
IP0 = [-1, 87.1, -2, 126.5, -strumD / 2, 51.7, -45]
IP1 = [2.1, 86.3, 0, 127.1, -strumD / 2, 50.1, -45]
IP2 = [1.5, 81.6, 0.0, 120, -strumD / 2, 54.2, -45]
IP3 = [2.5, 81, 0, 117.7, -strumD / 2, 50.5, -45]
IP4 = [-1.6, 81.8, 0, 120, -strumD / 2, 50.65, -45]
IP = [IP0, IP1, IP2, IP3, IP4]

# Regular Arms
arm0 = XArmAPI('192.168.1.208')
arm1 = XArmAPI('192.168.1.226')
arm2 = XArmAPI('192.168.1.244')
arm3 = XArmAPI('192.168.1.203')
arm4 = XArmAPI('192.168.1.237')
arms = [arm0, arm1, arm2, arm3, arm4]

# Drummer Arm
armDrum = XArmAPI('192.168.1.204')
drums = [armDrum]

# Initialize
q0 = Queue()
q1 = Queue()
q2 = Queue()
q3 = Queue()
q4 = Queue()
qList = [q0, q1, q2, q3, q4]

# Drum Queue
drumQ = Queue()

xArm0 = Thread(target=strummer, args=(q0, 0,))  # num 2
xArm1 = Thread(target=strummer, args=(q1, 1,))  # num 4
xArm2 = Thread(target=strummer, args=(q2, 2,))  # num 1
xArm3 = Thread(target=strummer, args=(q3, 3,))  # num 3
xArm4 = Thread(target=strummer, args=(q4, 4,))  # num 5
xArmDrum = Thread(target=drummer, args=(drumQ, 5,))


def startThreads():
    xArm0.start()
    xArm1.start()
    xArm2.start()
    xArm3.start()
    xArm4.start()
    xArmDrum.start()


# Time delay before playing
defaultDelayArray = np.array([[0.15, 0.15, 0.15, 0.15, 0.15, 0.0, 0.0], [
    0.1, 0.15, 0.1, 0.15, 0.125, 0.0, 0.0]])

# INDEX TO ROBOT MAPPING
# 0 => 1
# 1 => 3
# 2 => 0
# 3 => 2
# 4 => 4
delayArray = {
    'C': np.array([[0.0, 0.4, 0.0, 0.1, 0.7],
                   [0.0, 0.4, 0.0, 0.1, 0.7]]),
    'F': np.array([[0.0, 0.1, 0.7, 0.4, 0.0],
                   [0.0, 0.1, 0.7, 0.4, 0.0]]),
    'G': np.array([[0.0, 0.0, 0.1, 0.4, 0.7],
                   [0.0, 0.0, 0.1, 0.4, 0.7]])

    # 'C': np.array([[0.0, 0.4, 0.0, 0.1, 0.7],
    #                [0.0, 1.3, 0.0, 1.0, 1.6]]),
    # 'F': np.array([[0.0, 0.1, 0.7, 0.4, 0.0],
    #                [0.0, 1.1, 1.6, 1.3, 0.0]]),
    # 'G': np.array([[0.0, 0.0, 0.1, 0.4, 0.7],
    #                [0.0, 0.0, 0.1, 0.4, 0.7]])

    # 'C': np.array([[0.0, 0.1, 0.0, 0.4, 0.7, 0.0, 0.0],
    #                [0.0, 0.1, 0.0, 0.4, 0.7, 0.0, 0.0]]),
    # 'F': np.array(([[0.1, 0.4, 0.0, 0.0, 0.7, 0.0, 0.0],
    #                [1.0, 1.3, 0.0, 0.0, 1.6, 0.0, 0.0]])),
    # 'G': np.array(([[0.0, 0.0, 0.1, 0.4, 0.7, 0.0, 0.0],
    #                [0.0, 0.0, 0.1, 0.4, 0.7, 0.0, 0.0]]))
}
