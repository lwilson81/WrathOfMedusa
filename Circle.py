import os
import sys
import time
import numpy as np
import math

#from rtpmidi import RtpMidi
#from pymidi import server
from queue import Queue
from threading import Thread

from trajectoryGen import spline_poly
from xarm.wrapper import XArmAPI



def circleSetup(arms):

    for a in range(len(arms)):
        arms[a].set_simulation_robot(on_off=False)
        arms[a].motion_enable(enable=True)
        arms[a].clean_warn()
        arms[a].clean_error()
        arms[a].set_mode(0)
        arms[a].set_state(0)
        # curIP = IP[a]
        # arms[a].set_servo_angle(angle=curIP, wait=False, speed=10, acceleration=0.25, is_radian=False)

        arms[a].set_servo_angle(angle=[-12.2, 52.8, 26.5, 44, 11.9,-77.5, 69.3], wait=False, speed=10, acceleration=0.25, is_radian=False)



def drumbot(trajz, trajp, arm):
    track_time = time.time()
    initial_time = time.time()
    for i in range(len(trajz)):
        mvpose = [492, 0, trajz[i], 180, trajp[i], 0]
        arms[0].set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        while track_time < initial_time + 0.004:
            track_time = time.time()
            time.sleep(0.0001)
        initial_time += 0.004

def drummer(inq, num):
    # drumQ.put(1)
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


#
def livetraj(inq, robot):
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

    test = True

    while True:
        goal = inq.get()
        #print("moving", robot)
        q_i = p
        q_dot_i = 0
        q_dotdot_i = 0
        q_f = goal
        i = 0
        # or dancet != 0
        while (i <= len(t_array) or dancet != 0):
            start_time = time.time()
            if inq.empty() == False:
                goal = inq.get()
                #print("switch bot", robot)
                q_i = p
                q_dot_i = v
                q_dotdot_i = 0
                q_f = goal
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


            #48.0
            #0.0
            #-22.0
            xwave = -np.cos(3*dancet) * 48
            ywave = -np.sin(3*dancet) * 50
            zwave = np.cos(3*dancet) * 22
            #xwave = 0
            #ywave = 0
            #zwave = 0


            # mvpose = [362 + xwave, 67.2 + ywave, 102 + zwave, -111.2, 0, -90.2]
            mvpose = [425 + xwave, 17.6 + ywave, 102 + zwave, -111.2, 0, -90.2]


            if test:
                print(xwave)
                print(ywave)
                print(zwave)
                arms[robot].set_servo_cartesian(mvpose, speed=10, mvacc=100)

                test = False
            else:
                arms[robot].set_servo_cartesian(mvpose, speed=100, mvacc=2000)

            # print(mvpose[2])
            tts = time.time() - start_time
            sleep = 0.004 - tts

            if tts > 0.004:
                sleep = 0


            # print(tts)
            time.sleep(sleep)
            i += 1
            # if t == 1:
            # print(t, p, v, a)
#         print("done")
# # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ROBOT = "xArms"
    PORT = 5004
    global IP
    # global arms


    IP = [40.7, 63.9, -40, 83.9, 177.1, 24.4, -54]
    IPcar = [589.1, 31.2, 40.6, -122.1, -7.2, -89.2] #ip cartesian



    arm0 = XArmAPI('192.168.1.204')

    arms = [arm0]
    # arms = [arm1]
    totalArms = len(arms)
    # setup()
    input("lets go")

    for a in arms:
        a.set_mode(1)
        a.set_state(0)

    q0 = Queue()
    qList = [q0]

    xArm0 = Thread(target=drummer, args=(q0, 0,))
    xArm0.start()

    #input("start RTP MIDI")
    #rtp_midi = RtpMidi(ROBOT, MyHandler(), PORT)
    #print("test")
    #rtp_midi.run()
    #print("test2")

    q0.put(1)

    # while True:
    #     q0.put(1)
    #     #xArm0 = Thread(target=drummer, args=(q0, 0,))
    #     #xArm0.start()
    #     time.sleep(22)

    while True:
        q0.put(1)
        time.sleep(10)