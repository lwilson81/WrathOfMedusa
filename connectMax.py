import random
import socket
import atexit  # for when server closes
import threading  # for server
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import queue

UDP_IP = "127.0.0.1"  # local IP
UDP_PORT = 3500  # port to retrieve data from Max

# make Queue -> .get() will call print_data -> .put() will put data into Queue
global received
# 0 is degree, 1 is velocity, 2 is chord name
received = queue.Queue()

############## functions to be mapped using dispatcher ################


def add_values_to_queue(name, *args):
    received.put((0, args[0]))  # add degree to Queue as int
    received.put((1, args[1]))  # add velocity to Queue as int
    received.put((2, args[2]))  # add chord to Queue as string


################ all function mappings made here #############
dispatcher = dispatcher.Dispatcher()  # dispatcher to send
dispatcher.map("/toPython", add_values_to_queue)
##############################################################

#velocity in max is [0, 127]
#slow = [0,42]
#medium = [43,85]
#fast = [86,127]


def get_velocity_range(velocity):
    if velocity in range(0, 43):
        return "slow"
    elif velocity in range(44, 86):
        return "medium"
    else:
        return "fast"

############# define server to be running in background ####################
def server():
    server = osc_server.ThreadingOSCUDPServer((UDP_IP, UDP_PORT), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    atexit.register(server.server_close())
threading.Thread(target=server, daemon=True).start() 
client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT) #client to send to other functions
#############################################################################

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

    # client to send to other functions
    client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)
    #############################################################################

    ############ functions to do things to data ##########################

    while True:
        instruction, value = received.get()  # get instruction and val from Queue

        if instruction == 0:
            print("degree:" + str(value))
        elif instruction == 1:
            print("velocity:" + str(value))
            print("range:" + str(get_velocity_range(value)))
        elif instruction == 2:
            print("chord:" + str(value))

        # dictionary mappings from value to movement

    # {C:move home, D left, E left, F left, G right, A right, B right, }
