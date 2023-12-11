import datetime as dt
import math

import pygame
from block import GetBlockStartTime
from predictor import Predictor



class OutputGen:
    xMax = 400
    yMax = 300

    blockMin = None
    blockMax = None
    blockWidth = None

    def __init__(self, sensors, weather, heating, predictor, targets, nest):
        self.sensors = sensors
        self.weather = weather
        self.heating = heating
        self.predictor = predictor
        self.targets = targets
        self.nest = nest

    def BlockX(self, block):
        x = 30 + (block - self.blockMin) * self.blockWidth

        return x

    def StatusText(self, surface, pos, font, text, colour):
        statusfg = font.render(text, False, colour)
        statusbg = font.render(text, False, (255, 255, 255))
        for x in range(-1, 2):
            for y in range(-1, 2):
                surface.blit(statusbg, (pos[0] + x, pos[1] + y))

        surface.blit(statusfg, (pos[0], pos[1]))

    def DotBackground(self, surface, p1, p2, pitch, colour):
        for x in range(p1[0], p2[0], pitch):
            for y in range(p1[1], p2[1], pitch):
                surface.set_at((x, y), colour)

    def Dots2(self, surface, color):
        for x in range(0, surface.get_width(), 2):
            for y in range(0, surface.get_width(), 2):
                surface.set_at((x, y), color)

    def Checker(self, surface, color):
        for x in range(0, surface.get_width(), 1):
            for y in range(x % 2, surface.get_width(), 2):
                surface.set_at((x, y), color)

    def DotLine(self, surface, start, end, colour, offset=0):
        x0 = int(start[0])
        y0 = int(start[1])
        x1 = int(end[0])
        y1 = int(end[1])

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = sy = 0

        if x0 < x1:
            sx = 1
        else:
            sx = -1
        if y0 < y1:
            sy = 1
        else:
            sy = -1

        err = dx - dy

        while True:
            if offset == 2:
                surface.set_at((x0, y0), colour)
                surface.set_at((x0 + 1, y0), colour)
                surface.set_at((x0, y0 + 1), colour)
                surface.set_at((x0 + 1, y0 + 1), colour)
            offset = offset + 1
            if offset > 3:
                offset = 0

            if (x0 == x1) and (y0 == y1):
                break

            e2 = 2 * err
            if e2 > -dy:
                err = err - dy
                x0 = x0 + sx

            if (x0 == x1) and (y0 == y1):
                # drawPoint(pic, col, x0, y0)
                break

            if e2 < dx:
                err = err + dx
                y0 = y0 + sy

        return offset

    def SmallDotLine(self, surface, start, end, colour, offset=0):
        x0 = int(start[0])
        y0 = int(start[1])
        x1 = int(end[0])
        y1 = int(end[1])

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = sy = 0

        if x0 < x1:
            sx = 1
        else:
            sx = -1
        if y0 < y1:
            sy = 1
        else:
            sy = -1

        err = dx - dy

        while True:
            if offset == 0:
                surface.set_at((x0, y0), colour)
            offset = offset + 1
            if offset > 1:
                offset = 0

            if (x0 == x1) and (y0 == y1):
                break

            e2 = 2 * err
            if e2 > -dy:
                err = err - dy
                x0 = x0 + sx

            if (x0 == x1) and (y0 == y1):
                break

            if e2 < dx:
                err = err + dx
                y0 = y0 + sy

        return offset

    def ChartCoord(self, block, temp, minTemp, maxTemp):
        x = self.BlockX(block)
        y = 235 - ((temp - minTemp) / (maxTemp - minTemp)) * (35 * 5)
        return x, y

    def GenImage(self, surface, nowBlock):
        # fill background white
        white = (255, 255, 255)
        surface.fill(white)

        # setup colours
        white = (255, 255, 255)
        black = (0, 0, 0)
        red = (255, 0, 0)

        # setup fonts
        smallfont = pygame.font.Font("fonts/ChunkyDunk.ttf", 14)
        topDigitsFont = pygame.font.Font("fonts/Quicksand_Bold.otf", 38)
        topTitlesFont = pygame.font.Font("fonts/Quicksand_Bold.otf", 23)

        # pixel width of a single block
        self.blockWidth = (395 - 20) / (4 * 24)

        # blocks at far left and far right of the chart
        self.blockMin = nowBlock - (4 * 12)
        self.blockMax = nowBlock + (4 * 12)

        # X-Axis - draw time every 2 hours
        for t in range(self.blockMin, self.blockMax, 12):
            if t == nowBlock:
                pygame.draw.line(
                    surface, black, (self.BlockX(t), 235), (self.BlockX(t), 60)
                )
            else:
                self.SmallDotLine(
                    surface, (self.BlockX(t), 235), (self.BlockX(t), 60), black
                )

            timetext = dt.datetime.fromtimestamp(GetBlockStartTime(t)).strftime("%H:%M")
            txtsurf = smallfont.render(timetext, False, black)
            surface.blit(
                txtsurf,
                (self.BlockX(t) - txtsurf.get_width() // 2, 225 + txtsurf.get_height()),
            )

        # draw a solid line in the past with the actual internal temp

        # find min/max of temperatures to range the y-axis
        minTemp = 100
        maxTemp = -100
        for t in range(self.blockMin, nowBlock + 1):
            realTemp = self.sensors.GetTempAtTime(GetBlockStartTime(t))
            if realTemp > maxTemp:
                maxTemp = realTemp
            if realTemp < minTemp:
                minTemp = realTemp

        futureTemps = self.predictor.PredictFutureTemps(
            GetBlockStartTime(nowBlock), self.heating, self.blockMax + 1
        )

        for k in futureTemps.keys():
            if self.blockMin < k < self.blockMax:
                if futureTemps[k] > maxTemp:
                    maxTemp = futureTemps[k]
                if futureTemps[k] < minTemp:
                    minTemp = futureTemps[k]

        for k in self.targets.keys():
            if self.blockMin < k < self.blockMax:
                if self.targets[k] > maxTemp:
                    maxTemp = self.targets[k]
                if self.targets[k] < minTemp:
                    minTemp = self.targets[k]

        # extend the ranges a bit
        minTemp = math.floor(minTemp - 1)
        maxTemp = math.floor(maxTemp + 2)

        # draw values on the x-axis
        for i in range(0, 5):
            dispTemp = ((maxTemp - minTemp) / 5) * i + minTemp
            tempText = "{:2.1f}".format(dispTemp)
            txtsurf = smallfont.render(tempText, False, black)
            width = txtsurf.get_width()
            surface.blit(txtsurf, (28 - width, 225 - (i * 35)))

        # draw a solid red line with the target temperatures
        for b in range(self.blockMin, self.blockMax):
            x, y = self.ChartCoord(b, self.targets[b], minTemp, maxTemp)
            x2, y2 = self.ChartCoord(b + 1, self.targets[b + 1], minTemp, maxTemp)
            # horizontal line to the end of the block
            pygame.draw.line(surface, red, (x, y), (x2, y), 2)
            # vertical line to the start of the next block
            pygame.draw.line(surface, red, (x2, y), (x2, y2), 2)

        # draw a dotted line in the future with the predicted internal temp
        offset = 0
        for b in range(nowBlock, self.blockMax):
            x, y = self.ChartCoord(b, futureTemps[b], minTemp, maxTemp)
            x2, y2 = self.ChartCoord(b + 1, futureTemps[b + 1], minTemp, maxTemp)
            offset = self.DotLine(surface, (x, y), (x2, y2), black, offset)


        testPredictions = Talse
        if testPredictions:
            for i in range(nowBlock - 12*4, nowBlock, 4*3):
                startBlock = i
                startTemp = self.sensors.GetTempAtTime(GetBlockStartTime(i))
                myPred = Predictor(self.weather, startTemp)
                ft = myPred.PredictFutureTemps(GetBlockStartTime(i), self.heating, self.blockMax + 1)
                # draw a dotted line in the future with the predicted internal temp
                offset = 0
                for b in range(startBlock, self.blockMax):
                    x, y = self.ChartCoord(b, ft[b], minTemp, maxTemp)
                    x2, y2 = self.ChartCoord(b + 1, ft[b + 1], minTemp, maxTemp)
                    offset = self.DotLine(surface, (x, y), (x2, y2), black, offset)

        # draw a solid line with the prior temperatures
        for b in range(self.blockMin, nowBlock):
            x, y = self.ChartCoord(
                b, self.sensors.GetTempAtTime(GetBlockStartTime(b)), minTemp, maxTemp
            )
            x2, y2 = self.ChartCoord(
                b + 1,
                self.sensors.GetTempAtTime(GetBlockStartTime(b + 1)),
                minTemp,
                maxTemp,
            )

            pygame.draw.line(surface, black, (x, y), (x2, y2), 2)

        # draw red bar at the bottom showing where heating will happen
        for b in range(self.blockMin, self.blockMax):
            if self.heating.GetPlannedHeating(b):
                x1 = self.BlockX(b)
                x2 = self.BlockX(b + 1)
                pygame.draw.line(surface, red, (x1, 229), (x2, 229), 6)

        # in the top area show:
        indoorTemp = self.sensors.GetTempAtTime(GetBlockStartTime(nowBlock))
        outdoorTemp = self.weather.GetTempForecast(GetBlockStartTime(nowBlock))

        intxt = "{:2.1f}".format(indoorTemp) + "\u00b0C"
        txtsurf = topDigitsFont.render(intxt, False, black)
        surface.blit(txtsurf, (5, 28))

        insidesurf = topTitlesFont.render("INSIDE", False, black)
        self.Checker(insidesurf, white)
        surface.blit(insidesurf, (5, 3))

        outtxt = "{:2.1f}".format(outdoorTemp) + "\u00b0C"
        txtsurf = topDigitsFont.render(outtxt, False, black)
        surface.blit(txtsurf, (153, 28))

        outsidesurf = topTitlesFont.render("OUTSIDE", False, black)
        self.Checker(outsidesurf, white)
        surface.blit(outsidesurf, (153, 3))

        timetxt = dt.datetime.fromtimestamp(GetBlockStartTime(nowBlock)).strftime(
            "%H:%M"
        )
        txtsurf = topDigitsFont.render(timetxt, False, black)
        surface.blit(txtsurf, (292, 28))

        timesurf = topTitlesFont.render("UPDATED", False, black)
        self.Checker(timesurf, white)
        surface.blit(timesurf, (292, 3))

        # status area at bottom of display
        self.DotBackground(surface, (0, 253), (400, 300), 3, black)

        if self.weather.GetStatus() is True:
            self.StatusText(surface, (3, 255), smallfont, "O Forecast", black)
        else:
            self.StatusText(surface, (3, 255), smallfont, "X Forecast", red)

        if self.sensors.GetStatus() is True:
            self.StatusText(surface, (3, 270), smallfont, "O Sensors", black)
        else:
            self.StatusText(surface, (3, 270), smallfont, "X Sensors", red)

        if self.nest.GetStatus() is True:
            self.StatusText(surface, (3, 285), smallfont, "O Nest", black)
        else:
            self.StatusText(surface, (3, 285), smallfont, "X Nest", red)

        count = 0
        for block in range(nowBlock - 24 * 4, nowBlock):
            if self.heating.GetPlannedHeating(block) is True:
                count = count + 1
        h = (count * 15) / 60
        hourstr = str(dt.timedelta(hours=h)).rsplit(':', 1)[0]
        hourstr = hourstr.replace(":","h")
        self.StatusText(
            surface,
            (270, 285),
            smallfont,
            "Last 24h heat: " +hourstr + "m",
            black,
        )

        if self.heating.GetPlannedHeating(nowBlock):
            self.StatusText(surface, (168, 275), topTitlesFont, "ON", red)
        else:
            self.StatusText(surface, (162, 275), topTitlesFont, "OFF", black)

        self.StatusText(surface, (160, 260), smallfont, "HEATING", black)
