import socket
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import atexit   #for when server closes
import threading   #for server

UDP_IP = "127.0.0.1"       #local IP
UDP_PORT = 3500            #port to retrieve data from Max



dispatcher = dispatcher.Dispatcher()   #dispatcher to send 
dispatcher.map("/velocity", velocity)
dispatcher.map("/note_name", note_name)


def server():
    server = osc_server.ThreadingOSCUDPServer((IP, PORT_FROM_MAX), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    atexit.register(server.server_close())


threading.Thread(target=server, daemon=True).start() 

client = udp_client.SimpleUDPClient(UDP_IP, UDP_PORT) #client to send to other functions


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(UDP_PORT)
    data = data.decode("utf-8")[:3].strip() #convert from byte to string
    print("chord played: %s" % data)
    