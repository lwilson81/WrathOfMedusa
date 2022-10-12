import random
import socket
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import atexit  # for when server closes
import threading  # for server

UDP_IP = "127.0.0.1"  # local IP
UDP_PORT = 3500  # port to retrieve data from Max


dispatcher = dispatcher.Dispatcher()  # dispatcher to send
# dispatcher.map("/velocity", velocity)
# dispatcher.map("/note_name", note_name)


def setup():
    for a in arms:
        a.set_simulation_robot(on_off=False)
        # a.motion_enable(enable=True)
        a.clean_warn()
        a.clean_error()
        a.set_mode(0)
        a.set_state(0)
        moveToStart(a)


def rotate(arm, modifier):
    # replace with numpy and broadcasting for optimization
    home = [0.0, 0.0, 0.0, 1.57, 0.0, 0.0, 0.0]

    # 360 ==> 6.28
    # 180 ==> 3.14
    # 90  ==> 1.57
    # 45  ==> 0.79
    for i in range(7):
        home[i] += modifier * (random.random - 0.5)

    arm.set_servo_angle(angle=home, wait=False, speed=0.4,
                        acceleration=0.25, is_radian=True)


def rotate(modifier):
    # replace with numpy and broadcasting for optimization
    for arm in arms:
        home = [0.0, 0.0, 0.0, 1.57, 0.0, 0.0, 0.0]

        # 360 ==> 6.28
        # 180 ==> 3.14
        # 90  ==> 1.57
        # 45  ==> 0.79
        for i in range(7):
            home[i] += modifier * (random.random - 0.5)

        arm.set_servo_angle(angle=home, wait=False, speed=0.4,
                            acceleration=0.25, is_radian=False)


def moveToStart(a):
    a.set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                      is_radian=True)


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET,     # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))
    print("running")

    ROBOT = "xArms"
    PORT = 5003

    from xarm.wrapper import XArmAPI

    # arm0 = XArmAPI('192.168.1.237')
    # arm1 = XArmAPI('192.168.1.208')
    # arm2 = XArmAPI('192.168.1.244')
    # arm3 = XArmAPI('192.168.1.203')
    # arm4 = XArmAPI('192.168.1.236')
    # arm5 = XArmAPI('192.168.1.226')
    # arm6 = XArmAPI('192.168.1.242')
    # arm7 = XArmAPI('192.168.1.215')
    # arm8 = XArmAPI('192.168.1.234')
    # arm9 = XArmAPI('192.168.1.237')
    # arm10 = XArmAPI('192.168.1.204')
    # arms = [arm0]
    arms = []

    while True:
        data, addr = sock.recvfrom(UDP_PORT)
        data = data.decode("utf-8").strip()  # convert from byte to string
        print("chord played: %s" % data)
        # rotate()
