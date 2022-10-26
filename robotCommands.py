import time
import numpy as np

from xarm import XArmAPI

global IP
global arms
global strumD
global speed
global notes
trajValue = False
ROBOT = "xArms"
PORT = 5003

strumD = 30
speed = 0.25

IP0 = [-1, 87.1, -2, 126.5, -strumD/2, 51.7, -45]
IP1 = [2.1, 86.3, 0, 127.1, -strumD/2, 50.1, -45]
IP2 = [1.5, 81.6, 0.0, 120, -strumD/2, 54.2, -45]
IP3 = [2.5, 81, 0, 117.7, -strumD/2, 50.5, -45]
IP4 = [-1.6, 81.8, 0, 120, -strumD/2, 50.65, -45]
#IP = [IP0, IP1, IP2, IP3, IP4]
IP = [IP4, IP1, IP2, IP3, IP4] # for testing

def fifth_poly(q_i, q_f, t):
    # time/0.005
    traj_t = np.arange(0, t, 0.004)
    dq_i = 0
    dq_f = 0
    ddq_i = 0
    ddq_f = 0
    a0 = q_i
    a1 = dq_i
    a2 = 0.5 * ddq_i
    a3 = 1 / (2 * t ** 3) * (20 * (q_f - q_i) - (8 * dq_f +
                                                 12 * dq_i) * t - (3 * ddq_f - ddq_i) * t ** 2)
    a4 = 1 / (2 * t ** 4) * (30 * (q_i - q_f) + (14 * dq_f +
                                                 16 * dq_i) * t + (3 * ddq_f - 2 * ddq_i) * t ** 2)
    a5 = 1 / (2 * t ** 5) * (12 * (q_f - q_i) -
                             (6 * dq_f + 6 * dq_i) * t - (ddq_f - ddq_i) * t ** 2)
    traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * \
        traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
    return traj_pos


# uptraj = fifth_poly(-strumD/2, strumD/2, speed)
# downtraj = fifth_poly(strumD/2, -strumD/2, speed)
# trajQueue = [uptraj, downtraj]

# arm1 = XArmAPI('192.168.1.208')
# arm2 = XArmAPI('192.168.1.244')
# arm3 = XArmAPI('192.168.1.203')
# arm4 = XArmAPI('192.168.1.236')
# arm5 = XArmAPI('192.168.1.226')
# arm6 = XArmAPI('192.168.1.242')
# arm7 = XArmAPI('192.168.1.215')
# arm8 = XArmAPI('192.168.1.234')
arm9 = XArmAPI('192.168.1.237')
# arm10 = XArmAPI('192.168.1.204')

# arms = [arm9]
arms = [arm9]


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


def moveToStart(index):
    print(index)
    arms[index].set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)


def moveToStrumPos(index):
    arms[index].set_servo_angle(angle=IP[index], wait=False, speed=0.4, acceleration=0.25,
                                is_radian=True)


def strumbot(numarm, traj):
    pos = IP[numarm]
    j_angles = pos
    track_time = time.time()
    initial_time = time.time()
    for i in range(len(traj)):
        # run command
        start_time = time.time()
        j_angles[4] = traj[i]
        arms[numarm].set_servo_angle_j(angles=j_angles, is_radian=False)

        while track_time < initial_time + 0.004:
            track_time = time.time()
            time.sleep(0.0001)
        initial_time += 0.004



def strum():
    global trajValue
    print("strummed")
    uptraj = fifth_poly(-strumD / 2, strumD / 2, speed)
    downtraj = fifth_poly(strumD/2, -strumD/2, speed)
    trajQueue = [uptraj, downtraj]

        # moveToStrumPos(0)
    arms[0].set_mode(1)
    arms[0].set_state(0)
    strumbot(0, trajQueue[int(trajValue)])
    trajValue = not trajValue
    # arms[0].set_servo_angle(angle=[-1.6, 81.8, 0, 120, 20, 50.65, -45],  is_radian=False, wait=False, speed=10, acceleration=0.25)

def getArms():
    return arms


def getIPs():
    return IP
