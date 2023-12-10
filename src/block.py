# returns the 15-min block identifier for the given time
def GetBlockNum(time):
    return int((time // 60) // 15)


def GetBlockStartTime(block):
    return float((block * 60) * 15)
