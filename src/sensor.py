import shelve
import time


class BME280Sensor:
    bme280 = None

    def __init__(self):
        from smbus2 import SMBus
        from bme280 import BME280

        bus = SMBus(1)
        self.bme280 = BME280(i2c_dev=bus)
        self.bme280.setup(mode="forced")
        print("Sensor wait time...")
        time.sleep(5)
        print("Sensor ready.")

    def GetCurrentTemp(self):
        try:
            currentTemp = self.bme280.get_temperature() - 0.2
            print(currentTemp)
            return currentTemp
        except Exception as e:
            print(e)
            return 0


class MockSensor:
    def GetCurrentTemp(self):
        currentTemp = 20.5
        return currentTemp


class Sensors:
    DBNAME = "sensors"

    data = {}
    status = True  # false if mock sensors are used or error from real sensor
    mySensor = None

    def __init__(self):
        time.time()
        with shelve.open(self.DBNAME) as db:
            dkeys = db.keys()
            for k in dkeys:
                t = int(k)

                self.data[t] = db[k]

        try:
            from smbus2 import SMBus
            from bme280 import BME280

            bus = SMBus(1)
            bme280 = BME280(i2c_dev=bus)
            bme280.setup()

            self.mySensor = BME280Sensor()
        except Exception as e:
            print(e)
            self.mySensor = MockSensor()
            self.status = False

    # read the current value from the sensor
    def GetCurrentTemp(self):
        temp = self.mySensor.GetCurrentTemp()

        if temp == 0:
            self.status = False

        return temp

    def GetStatus(self):
        return self.status

    def UpdateSensors(self, seconds):
        currentTemp = self.GetCurrentTemp()

        seconds = int(seconds)

        self.data[seconds] = currentTemp

        # write the value to the db
        with shelve.open(self.DBNAME) as db:
            for k in self.data:
                db[str(k)] = self.data[k]

    # returns the temp closest to the current time
    def GetLatestTemp(self):
        temp = self.GetTempAtTime(time.time())
        return temp

    def GetTempAtTime(self, seconds):
        # if the exact time is in the db, return it right away
        if seconds in self.data:
            return self.data[seconds]

        # otherwise we'll just find the closests
        closest = -1
        bestDif = 9999999999
        for k in self.data.keys():
            dif = abs(k - seconds)
            if dif < bestDif:
                bestDif = dif
                closest = k
        if closest != -1:
            return self.data[closest]

        # must be an empty list
        return 0
