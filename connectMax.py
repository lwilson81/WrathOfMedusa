from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import atexit   #for when server closes
import threading   #for server
import queue

UDP_IP = "127.0.0.1"       #local IP
UDP_PORT = 3500            #port to retrieve data from Max

# make Queue -> .get() will call print_data -> .put() will put data into Queue
global received
# 0 is degree, 1 is velocity, 2 is chord name
received = queue.Queue()

############## functions to be mapped using dispatcher ################
def print_data(name, *args):
    # receive.put(args[0])
    print(args)


def add_values_to_queue(name, *args):
    received.put((0, args[0]))  # add degree to Queue as int
    received.put((1, args[1]))  # add velocity to Queue as int
    received.put((2, args[2]))  # add chord to Queue as string



################ all function mappings made here #############
dispatcher = dispatcher.Dispatcher()   #dispatcher to send 
dispatcher.map("", add_values_to_queue)
##############################################################

#velocity in max is [0, 127]
#slow = [0,42]
#medium = [43,85]
#fast = [86,127]
def get_velocity_range(velocity):
    if velocity in range(0,43):
        return "slow"
    elif velocity in range(44,86):
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



############ functions to do things to data ##########################


while True:
    instruction, value = received.get()  # get instruction and val from Queue
    
    if instruction ==   0:
        print("degree:" + str(value))
    elif instruction == 1:
        print("velocity:" + str(value))
        print("range:" + str(get_velocity_range(value)))
    elif instruction == 2:
        print("chord:" + str(value))

    # dictionary mappings from value to movement
    



# {C:move home, D left, E left, F left, G right, A right, B right, }
    