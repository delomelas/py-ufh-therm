import time
import datetime

import pygame

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

minBlock = None
maxBlock = None

# TODO
# some way to control it...
# - switch on/off (or at least skip setting the boiler)
# - set new targets? will need a UI for this

def SetupTargets():
    # time, temperature pairs
    setPoint = [[9, 19.5], [10, 20.0], [22, 18]]
    # holidaySetPoint = [[10, 18], [22, 16.0]]
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

        if temp is None:
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

targets = SetupTargets()

plan = optimiser.GetHeatingPlan(now, targets)

outputgen = OutputGen(sensor, weather, plan, predictor, targets, nest)

futureBlocks = 0
for block in plan.heat.keys():
    if plan.GetPlannedHeating(block) and nowBlock <= block < maxBlock:
        futureBlocks = futureBlocks + 1

print("Total heating blocks planned: " + str(futureBlocks))

# if heating for the current block has changed, try to communicate with the nest
# if plan.GetPlannedHeating(nowBlock) != plan.GetPlannedHeating(nowBlock - 1):
if plan.GetPlannedHeating(nowBlock) is True:
    print("Switching heating on.")
    nest.setNestTargetTemp(22.0)
else:
    print("Switching heating off.")
    nest.setNestTargetTemp(12)

# all done, output to the status screen

pygame.font.init()
surface = pygame.Surface((400, 300))
outputgen.GenImage(surface, nowBlock)

pygame.image.save(surface, "image.bmp")

SurfaceToInky(surface)

# store the plan for the current block
heating.PutPlannedHeating(nowBlock, plan.GetPlannedHeating(nowBlock))
heating.Store()
