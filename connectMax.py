import atexit
from shutil import move  # for when server closes
import threading  # for server
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import queue

from Mode import Mode, getMode
from robotCommands import moveToStart, playPattern, setup, startThreads, strummer, turnOffLive, turnOnLive, rotateRandomly

# UDP_IP = "127.0.0.1"  # local IP
UDP_IP = "0.0.0.0"  # hivemind IP
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


############# define server to be running in background ####################
def server():
    server = osc_server.ThreadingOSCUDPServer((UDP_IP, UDP_PORT), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    atexit.register(server.server_close())


threading.Thread(target=server, daemon=True).start()

# client to send to other functions
client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)

if __name__ == "__main__":
    # setup()
    # startThreads()
    client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT)

    # Default Mode
    mode = Mode.DANCE

    while True:
        # MANUAL CONTROLS
        print("Enter a value")
        manual_value = str(input())

        if Mode.from_str(manual_value):
            temp = Mode.from_str(manual_value)
            if mode != temp:
                if temp.value % 2 == 0:
                    turnOffLive()
                else:
                    turnOnLive()
                mode = temp
                print("New Mode: " + str(mode))
            else:
                print("Already in " + str(mode))

        else:
            # Carry Out Commands
            if mode == Mode.DANCE:
                rotateRandomly(int(manual_value))

            elif mode == Mode.ARPEGGIOS:
                playPattern(manual_value)

            elif mode == Mode.STRUM:
                print("Not yet implemented")

        # playPattern(manual_value)

        # testDrum()

        # KEYBOARD CONTROLS
        # instruction, value = received.get()  # get instruction and val from Queue
        # print(value)

        # playPattern(value)
        # print(instruction)
        # degree = 1

        # if instruction == 0:
        # print("degree:" + str(value))
        # degree = value
        # rotateRandomly(value)

        # elif instruction == 1:  # velocity instruction is 1
        # i = 1
        # print("velocity:" + str(value))
        # print("range:" + str(getVelocityRange(value)))

        # if instruction == 2:  # chord instruction is 2
        #     playPattern(value)
