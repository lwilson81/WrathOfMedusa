import time
import numpy as np
import random

import serial

from helpers import chordDegreeToModifier
# from lights import testList, sendSyncVal, testSend
from xarm import XArmAPI
from queue import Queue
from threading import Thread
from trajectoryGen import fifth_poly, spline_poly
from Circle import circleSetup


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

    circleSetup(drums)
    # armDrum.set_simulation_robot(on_off=False)
    # armDrum.motion_enable(enable=True)
    # armDrum.clean_warn()
    # armDrum.clean_error()
    # drumRobotToCirclePos()
    print("Ready to start.")


# Start Positions (not Live mode)
def moveToStart(index):
    arms[index].set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)


def moveToStrumPos(index):
    arms[index].set_servo_angle(angle=IP[index], wait=False,
                                speed=20, acceleration=0.25, is_radian=False)


def drumRobotToCirclePos():
    armDrum.set_simulation_robot(on_off=False)
    armDrum.motion_enable(enable=True)
    armDrum.clean_warn()
    armDrum.clean_error()
    armDrum.set_mode(0)
    armDrum.set_state(0)
    armDrum.set_servo_angle(angle=[-12.2, 52.8, 26.5, 44, 11.9, -77.5, 69.3], wait=False, speed=10, acceleration=0.25,
                            is_radian=False)
    print("Drummer is ready to circle")

    waitForDrummer()

    armDrum.set_mode(1)
    armDrum.set_state(0)


def drumRobotToDrumPos():
    armDrum.set_mode(0)
    armDrum.set_state(0)
    armDrum.set_servo_angle(angle=[-12.2, 52.8, 26.5, 44, 11.9, -77.5, 69.3], wait=False, speed=10, acceleration=0.25,
                            is_radian=False)
    print("Drummer is ready to drum")

    waitForDrummer()

    armDrum.set_mode(1)
    armDrum.set_state(0)



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


def waitForDrummer():
    not_safe_to_continue = True
    while not_safe_to_continue:
        not_safe_to_continue = False
        if armDrum.get_is_moving():
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
        print("Strum Command Received for Robot " + str(robotNum))

        strumDirection = i % 2

        time.sleep(delayArray[variation][strumDirection, robotNum])
        lightQ.put(robotNum)
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


def testCircle():
    livetraj(0, 0)

def drummer(inq, num):
    drumQ.put(1)
    # trajz = spline_poly(325, 35, .08, .08, 0.01)
    # trajp = spline_poly(-89, -28, .08, .08, 0.01)
    #
    # trajz2 = spline_poly(325, 35, .08, .08, .1)
    # trajp2 = spline_poly(-89, -28, .08, .08, .1)
    #
    # trajz3 = spline_poly(325, 35, .08, .08, .15)
    # trajp3 = spline_poly(-89, -28, .08, .08, .15)
    #
    # i = 0
    # while True:
    #     i += 1
    #     play = inq.get()
    #
    #     # end of run indef
    #     if i % 3 == 1:
    #         drumbot(trajz, trajp, num)
    #
    #     elif i % 3 == 2:
    #         drumbot(trajz2, trajp2, num)
    #
    #     elif i % 3 == 0:
    #         drumbot(trajz3, trajp3, num)


def livetraj(inq, robot):
    waitForDrummer()

    for arm in drums:
        arm.set_mode(0)
        arm.set_state(0)

    waitForDrummer()


    tf = 2
    # q i
    # 0.2 * np.floor(xi / 0.2)
    # range is 200 to -200
    t0 = 0
    t = t0
    q_i = 0
    q_dot_i = 0
    q_dot_f = 0
    q_dotdot_i = 0
    q_dotdot_f = 0
    t_array = np.arange(0, tf, 0.006)
    p = 0
    v = 0
    a = 0
    dancet = 0

    i = 0
    # or dancet != 0
    print("okee")
    while (i <= len(t_array) or dancet != 0):
        print("dokee")
        start_time = time.time()
        # if inq.empty() == False:
        #     goal = inq.get()
        # print("switch bot", robot)
        q_i = p
        q_dot_i = v
        q_dotdot_i = 0
        # q_f = goal
        i = 0
        # IF YOU WANT TO ADD SPEED CHANGES THEN SWAP THE ABOVE LINES WITH THE BELOW LINES
        # # q should input an array of [*absolute* position of joint, time(in seconds) to reach there]
        # q_f = goal[0]
        # tf = goal[1]
        # t_array = np.arange(0, tf, 0.006)
        # print("switch")
        if i >= len(t_array):
            t = tf
            # if at end, append more time
            # t_array = np.append(t_array, tf+0.006)
            # print(t_array)
            dancet += 0.006
        else:
            t = t_array[i]
            dancet = t

        # amplitude returns sin wave to oscillate over

        # 48.0
        # 0.0
        # -22.0
        xwave = -np.cos(3 * dancet) * 48
        ywave = -np.sin(3 * dancet) * 50
        zwave = np.cos(3 * dancet) * 22
        # xwave = 0
        # ywave = 0
        # zwave = 0

        # mvpose = [362 + xwave, 67.2 + ywave, 102 + zwave, -111.2, 0, -90.2]
        mvpose = [425 + xwave, 17.6 + ywave, 102 + zwave, -111.2, 0, -90.2]

        arms[robot].set_servo_cartesian(mvpose, speed=100, mvacc=2000)

        # print(mvpose[2])
        tts = time.time() - start_time
        sleep = 0.004 - tts

        if tts > 0.004:
            sleep = 0

        # print(tts)
        time.sleep(sleep)
        i += 1


# def livetraj(inq, robot):
#     # DRUM CODE
#     trajz = spline_poly(325, 35, .08, .08, 0.01)
#     trajp = spline_poly(-89, -28, .08, .08, 0.01)
#
#     trajz2 = spline_poly(325, 35, .08, .08, .1)
#     trajp2 = spline_poly(-89, -28, .08, .08, .1)
#
#     trajz3 = spline_poly(325, 35, .08, .08, .15)
#     trajp3 = spline_poly(-89, -28, .08, .08, .15)
#
#     i = 0
#
#     # CIRCLE CODE
#     tf = 2
#     # q i
#     # 0.2 * np.floor(xi / 0.2)
#     # range is 200 to -200
#     t0 = 0
#     t = t0
#     q_i = 0
#     q_dot_i = 0
#     q_dot_f = 0
#     q_dotdot_i = 0
#     q_dotdot_f = 0
#     t_array = np.arange(0, tf, 0.006)
#     p = 0
#     v = 0
#     a = 0
#     dancet = 0
#
#
#     while True:
#         goal = inq.get()
#         if goal == 1:
#             i += 1
#
#             print("herear")
#             # end of run indef
#             if i % 3 == 1:
#                 drumbot(trajz, trajp, robot)
#
#             elif i % 3 == 2:
#                 drumbot(trajz2, trajp2, robot)
#
#             elif i % 3 == 0:
#                 drumbot(trajz3, trajp3, robot)
#
#         else:
#             # print("moving", robot)
#             q_i = p
#             q_dot_i = 0
#             q_dotdot_i = 0
#             q_f = goal
#             i = 0
#             # or dancet != 0
#             while drumQ.empty() and i <= len(t_array) or dancet != 0:
#                 start_time = time.time()
#                 # if inq.empty() == False:
#                 #     goal = inq.get()
#                 # print("switch bot", robot)
#                 q_i = p
#                 q_dot_i = v
#                 q_dotdot_i = 0
#                 q_f = goal
#                 i = 0
#                 # IF YOU WANT TO ADD SPEED CHANGES THEN SWAP THE ABOVE LINES WITH THE BELOW LINES
#                 # # q should input an array of [*absolute* position of joint, time(in seconds) to reach there]
#                 # q_f = goal[0]
#                 # tf = goal[1]
#                 # t_array = np.arange(0, tf, 0.006)
#                 # print("switch")
#                 if i >= len(t_array):
#                     t = tf
#                     # if at end, append more time
#                     # t_array = np.append(t_array, tf+0.006)
#                     # print(t_array)
#                     dancet += 0.006
#                 else:
#                     t = t_array[i]
#                     dancet = t
#
#                 # amplitude returns sin wave to oscillate over
#
#                 xwave = np.cos(3 * dancet) * 48
#                 ywave = np.sin(3 * dancet) * 50
#                 zwave = -np.cos(3 * dancet) * 22
#                 # xwave = 0
#                 # ywave = 0
#                 # zwave = 0
#
#                 mvpose = [425 + xwave, 17.6 + ywave, 102 + zwave, -111.2, 0, -90.2]
#
#                 armDrum.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
#                 # print(mvpose[2])
#                 tts = time.time() - start_time
#                 sleep = 0.004 - tts
#
#                 if tts > 0.004:
#                     sleep = 0
#
#                 # print(tts)
#                 time.sleep(sleep)
#                 i += 1
#                 # if t == 1:
#                 # print(t, p, v, a)


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
    # send arrm numbers
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

    elif 'D7' in chord:
        drumQ.put(0)

    elif 'D' in chord:
        drumQ.put(1)


arduino = serial.Serial('/dev/ttyACM0', 9600)


def lightController(temp):
    while True:
        # print("still true")
        if lightMode == 0:  # gradient mode
            # print("yes")
            sendSyncVal('gradient')
            listSend(getAngles(2), randList1)  # [2, 3, 4, 5])
            listSend(getAngles(0), randList2)  # [1, 2, 3, 4, 5, 6])
            listSend(getAngles(3), randList3)  # [1, 2, 3, 4, 5, 6])
            listSend(getAngles(1), randList4)  # [1, 2, 3, 4, 5, 6])
            listSend(getAngles(4), randList5)  # [2, 3, 4, 5])
        if lightMode == 1:  # flash mode
            # print("no")
            received = lightQ.get()
            sendSyncVal('flash')
            sendSyncVal(str(received + 1))


testList = [0, 100, 200, 300, 400, 500]


def createRandList(size):
    a = []
    for i in range(size):
        a.append(random.randint(0, 6))
    return a


randList1 = createRandList(4)
randList2 = createRandList(6)
randList3 = createRandList(6)
randList4 = createRandList(6)
randList5 = createRandList(4)


def getAngles(a):
    angles = arms[a].angles
    return angles


def listSend(listToSend,
             anglesToSend):  # Picks and sends indexes, defined by anglesToSend, of a 6 item list, defined by listToSend
    sentList = []
    j = 0
    for i in anglesToSend:
        sentList.append((round(listToSend[i] * 2.5 * 256 / 360)) % 256 + (i * 20))
        arduino.write(str(sentList[j]).encode())
        delay()
        j += 1
    # print(sentList)


def delay():
    time.sleep(0.013)


def sendSyncVal(value):
    arduino.write(value.encode())
    delay()
    # print("sent " + value)


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
global lightMode

ROBOT = "xArms"
PORT = 5003

lightMode = 0

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

# Light Queue
global lightQ
lightQ = Queue()

xArm0 = Thread(target=strummer, args=(q0, 0,))  # num 2
xArm1 = Thread(target=strummer, args=(q1, 1,))  # num 4
xArm2 = Thread(target=strummer, args=(q2, 2,))  # num 1
xArm3 = Thread(target=strummer, args=(q3, 3,))  # num 3
xArm4 = Thread(target=strummer, args=(q4, 4,))  # num 5
xArmDrum = Thread(target=drummer, args=(drumQ, 5,))
# xArmDrum = Thread(target=livetraj, args=(drumQ, 5,))

lights = Thread(target=lightController, args=(lightQ,))


def startThreads():
    xArm0.start()
    xArm1.start()
    xArm2.start()
    xArm3.start()
    xArm4.start()
    xArmDrum.start()
    lights.start()


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
