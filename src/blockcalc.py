
class BlockCalc:

    @staticmethod
    def GetBlockStartTime(block):
        return block * 15 * 60
    
    @staticmethod
    def GetBlockForTime(time):
        return int(time // (60 * 15))
