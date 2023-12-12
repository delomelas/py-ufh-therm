from blockcalc import BlockCalc


class Predictor:
    def __init__(self, weather, currentTemp):
        self.weather = weather
        self.currentTemp = currentTemp

    def PredictFutureTemps(self, nowTime, heating, maxBlock):
        prevTemp = self.currentTemp

        nowBlock = BlockCalc.GetBlockForTime(nowTime)

        predictedTemps = {}

        # TODO
        # Simple handling of solar gains
        # Between sunrise and sunset
        # Estimate a sunshine index - handle winter/autumn/spring/summer differently
        # Between sunrise and sunset, apply a curve
        # Apply a factor depending on if it's cloudy or clear sky

        predictedTemps[nowBlock] = prevTemp

        for block in range(nowBlock + 1, maxBlock):
            # get the forecast for the next block time
            time = BlockCalc.GetBlockStartTime(block)
            forecastTemp = self.weather.GetTempForecast(time)

            # calculate the effect of outside temperature
            # simple temperature gradient
            # todo: add windchill and effect of solar gains?
            newTemp = (forecastTemp - prevTemp) / 165 + prevTemp

            # add the underfloor heating to this block
            newTemp = heating.ApplyHeatingForBlock(block, newTemp)

            predictedTemps[block] = newTemp
            prevTemp = newTemp

        return predictedTemps
