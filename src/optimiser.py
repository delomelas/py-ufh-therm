import time
from block import GetBlockNum

from predictor import Predictor

# givem weather history, sensor data, heating history
# calculate and return the required heating plan starting from [time]

class Optimiser:

    def __init__(self, sensors, weather, heating):
        self.sensors = sensors
        self.weather = weather
        self.pastHeating = heating

    # returns the first block after minBlock which is below the target temp
    def GetFirstColdBlock(self, temps, targets, minBlock, maxBlock):
        for block in temps:
            if temps[block] < targets[block] and block >= minBlock and block <= maxBlock:
                return block
        return -1

    # returns all the blocks which are below the target temp
    def GetColdBlocks(self, temps, targets, minBlock, maxBlock):
        cold = []
        for block in temps:
            if temps[block] < targets[block] and block >= minBlock and block <= maxBlock:
                cold.append(block)

        return cold

    # returns the 
    def CountColdBlock(self, temps, targets, minBlock, maxBlock):
        return len(self.GetColdBlocks(temps, targets, minBlock, maxBlock))

    def GetHeatingPlan(self, nowTime, targets):
        benchmark1 = time.time()
        currentTemp = self.sensors.GetLatestTemp()

        predictor = Predictor(self.weather, currentTemp)

        # base out initial predictions on the known past heating
        heatingPlan = self.pastHeating.Clone()

        maxBlock = GetBlockNum(nowTime) + (4 * 15)
        nowBlock = GetBlockNum(nowTime)

        # calculate predicted tamps to begin with
        temps = predictor.PredictFutureTemps(nowTime, heatingPlan, maxBlock)
        coldBlocks = self.GetColdBlocks(temps, targets, nowBlock, maxBlock)

        

        # for each block predicted to be cold
        for coldBlock in reversed(coldBlocks):
            # if other heating has fixed this block, we can move on
            if (temps[coldBlock] > targets[coldBlock]):
                continue
            
            # now try to find some heating that will maximally heat this cold block
            bestBlock = -1
            bestHeatIncrease = 0

            # test each block that could have an impact on this cold block
            startSearch = max(nowBlock, coldBlock - heatingPlan.heatImpactBlocks)
                
            for testBlock in (range(startSearch, coldBlock)):
                testHeating = heatingPlan.Clone()

                # if it's already heated, we can move on
                if testHeating.GetPlannedHeating(testBlock) == True:
                    continue
                
                testHeating.PutPlannedHeating(testBlock, True)
                newTemps = predictor.PredictFutureTemps(nowTime, testHeating, maxBlock)

                # what difference has this made to the heating?
                dif = newTemps[coldBlock] - temps[coldBlock]

                if (dif > bestHeatIncrease):
                    bestBlock = testBlock
                    bestHeatIncrease = dif

            # found a block to add, add it
            if (bestBlock >= 0):
                heatingPlan.PutPlannedHeating(bestBlock, True)
                
                # update the prediction based on this new plan
                temps = predictor.PredictFutureTemps(nowTime, heatingPlan, maxBlock)

        benchmark2 = time.time()

        # now optimise the heating plan by seeing if we can remove any heating
        # blocks without any targets going under
        removed = 0
        optiPlan = heatingPlan.Clone()
        for testBlock in range(nowBlock, maxBlock):
            if optiPlan.GetPlannedHeating(testBlock) == False:
                continue
            temps = predictor.PredictFutureTemps(nowTime, optiPlan, maxBlock)
            c1 = self.CountColdBlock(temps, targets, nowBlock, maxBlock)

            newOptiPlan = optiPlan.Clone()
            newOptiPlan.PutPlannedHeating(testBlock, False)
            temp2 = predictor.PredictFutureTemps(nowTime, newOptiPlan, maxBlock)
            c2 = self.CountColdBlock(temp2, targets, nowBlock, maxBlock)
            if (c2 <= c1):
                removed = removed + 1
                optiPlan = newOptiPlan.Clone()
                    
        print("Heating optimisation - blocks removed: " + str(removed))

        benchmark3 = time.time()

        print("Heating generation: " + str(benchmark2 - benchmark1))
        print("Heating optimisation: " + str(benchmark3 - benchmark2))
        
        return optiPlan
    
