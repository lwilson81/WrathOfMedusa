import random
from robotCommands import getArms, getIPs, fifth_poly, arms, timeToMove, movebot, poseToPose

def chordDegreeToModifer(chordDegree):
    return (chordDegree - 1) * 0.4


def rotateRandomly(chordDegree):
    arm = getArms()[0]
    home = [0.0, 0.0, 0.0, 1.57, 0.0, 0.0, 0.0]
    
    modifier = chordDegreeToModifer(chordDegree)

    # TODO: replace with numpy and broadcasting for optimization
    for i in range(7):
        home[i] += modifier * (random.random() - 0.5)

    trajectories = poseToPose(arms[0].angles, [v*57.296 for v in home], timeToMove)
    # print(arms[0].angles, [v*57.296 for v in home],)
    # print(trajectories)
    movebot(1, trajectories)



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
