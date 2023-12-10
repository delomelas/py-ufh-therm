from sensor import Sensors
from weather import Weather
from heating import Heating
from outputgen import OutputGen
from block import GetBlockNum
from block import GetBlockStartTime
from predictor import Predictor
from optimiser import Optimiser

from myinky import SurfaceToInky

from mynest import Nest

import pygame
import time
import datetime

# fix UTC times
# set NEST value as appropriate
# - if current heating block differs from past heating block,
# - attempt to conact the nest and set the temp
# - if we want the heating on, set the target temp to 22
# - if we want the heating off, set the target temp to 12

def SetupTargets(minBlock, maxBlock):

    # time, temperature pairs
    setPoint = [[9, 20.0], [17, 20.5], [21, 20.0], [22, 18.0]]

    targets = {}
    
    for t in range(minBlock, maxBlock):
        blockTime = GetBlockStartTime(t)
        hourstr = datetime.datetime.fromtimestamp(blockTime).strftime("%H")
        hours = int(hourstr)

        # work out which targets are either side of this point
        temp = None
        for point in setPoint:
            if hours >= point[0]:
                temp = point[1]

        if temp == None:
            temp = setPoint[-1][1]
        
        targets[t] = temp

    return targets


sensor = Sensors()
now = time.time()
sensor.UpdateSensors(now)

weather = Weather()
weather.UpdateWeather()

nest = Nest()
   
temp = sensor.GetLatestTemp()
predictor = Predictor(weather, temp)

heating = Heating()
heating.Load()

optimiser = Optimiser(sensor, weather, heating)

nowBlock = GetBlockNum(now)
minBlock = nowBlock - (15 * 4)
maxBlock = nowBlock + (15 * 4)

targets = SetupTargets(minBlock, maxBlock)

plan = optimiser.GetHeatingPlan(now, targets)

outputgen = OutputGen(sensor, weather, plan, predictor, targets, nest)

futureBlocks = 0
for block in plan.heat.keys():
    if plan.GetPlannedHeating(block) and block < maxBlock:
        futureBlocks = futureBlocks + 1
    
print ("Total heating blocks planned: " + str(futureBlocks))

# if heating for the current block has changed, try to communicate with the nest
#if plan.GetPlannedHeating(nowBlock) != plan.GetPlannedHeating(nowBlock - 1):
if plan.GetPlannedHeating(nowBlock) == True:
    print("Switching heating on.")
    nest.setNestTargetTemp(22.0)
else:
    print("Switching heating off.")
    nest.setNestTargetTemp(12)
   

# all done, output to the status screen

pygame.font.init()
surface = pygame.Surface((400,300))
outputgen.GenImage(surface, nowBlock)

pygame.image.save(surface, "image.bmp")

SurfaceToInky(surface)

# store the plan for the current block
heating.PutPlannedHeating(nowBlock, plan.GetPlannedHeating(nowBlock))
heating.Store()

 

