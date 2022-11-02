import random
from robotCommands import getArms, getIPs


def chordDegreeToModifer(chordDegree):
    return (chordDegree - 1) * 0.4


def rotateRandomly(chordDegree):
    arm = getArms()[0]
    arm.set_mode(0)
    arm.set_state(0)
    home = [0.0, 0.0, 0.0, 1.57, 0.0, 0.0, 0.0]
    
    modifier = chordDegreeToModifer(chordDegree)

    # TODO: replace with numpy and broadcasting for optimization
    for i in range(7):
        home[i] += modifier * (random.random() - 0.5)

    arm.set_servo_angle(angle=home, wait=False, speed=0.4,
                        acceleration=0.25, is_radian=True)


# def rotateRandomly(chordDegree):
#     print("rotated randomly")
#     arms = getArms()
#     IP = getIPs()
#     modifier = chordDegreeToModifer(chordDegree)
#
#     # TODO: replace with numpy and broadcasting for optimization
#     for i in range(len(arms)):
#         currentIP = IP[i]
#
#         for j in range(7):
#             currentIP[j] += modifier * (random.random() - 0.5)
#
#         arms[i].set_servo_angle(angle=currentIP, wait=False, speed=0.4,
#                                 acceleration=0.25, is_radian=True)


# velocity in Max is [0, 127]
# slow = [0,42]
# medium = [43,85]
# fast = [86,127]
def getVelocityRange(velocity):
    if velocity in range(0, 43):
        return "slow"
    elif velocity in range(44, 86):
        return "medium"
    else:
        return "fast"
