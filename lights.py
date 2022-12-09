#from xarm.wrapper import XArmAPI
import serial
import time

from robotCommands import getArms

mode = 1
#arduino = serial.Serial('com4',9600)    # for PC
#arduino = serial.Serial('/dev/ttyACM0',9600)   # for linux
#arduino.timeout = 0.01
#arm1 = XArmAPI('192.168.1.244')
#arm2 = XArmAPI('192.168.1.208')
#arm3 = XArmAPI('192.168.1.203')
#arm4 = XArmAPI('192.168.1.226')a
#arm5 = XArmAPI('192.168.1.237')
#arms = [arm1, arm2, arm3, arm4, arm5]
#arm3 = XArmAPI('192.168.1.208')
testList = [0,100,200,300,400,500]
arms = getArms()

def switchMode(value):
    mode = value

def sendSyncVal(value):
    arduino.write(value.encode())
    delay()
    print("sent " + value)


def listSend(listToSend, anglesToSend):
    sentList = []
    j = 0
    for i in anglesToSend:
        sentList.append((round(listToSend[i]*256/360)) % 256)
        arduino.write(str(sentList[j]).encode())
        delay()
        j += 1
    print(sentList)
    #delay()

def getAngles(a):
    angles = arms[a].angles
    return angles

# def getAnglesHardCoded():
#     angles = arm3.angles
#     return angles

def intable(string):
    try:
        int(string)
        return True
    except:
        return False

def testSend():
    testVal = input("whatchu want??? ")
    if intable(testVal) == True:
        arduino.write(testVal.encode())
        print("gotchu fam")
    else:
        if testVal == "stop":
            return "stop"
        else:
            print("ayo???")

# you can probably send 6 consecutive numbers and then do the time sleep
data = [0, 0, 0, 0, 0, 0]

def createList():
    for i in range(6):
        data[i] = manualInput(i)
    return data

def manualInput(index):
    val = input(str(index + 1) + ": ")
    if intable(val) == False:
        print("bruh")
        manualInput(index)
    else:
        return int(val)

def delay():
    time.sleep(0.005)


while True:
    #get some data from other script
    # if data == 0:
    if mode == 0: #gradient mode
        sendSyncVal('gradient')
        listSend(testList, [0,1,2,3])
        listSend(testList, [0,1,2,3,4,5])
        listSend(testList, [0,1,2,3,4,5])
        listSend(testList, [0,1,2,3,4,5])
        listSend(testList, [0,1,2,3])
    if mode == 1: #flash mode
        sendSyncVal('flash')
        testSend()
