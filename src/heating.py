import shelve


# Stores both a record of prior hearing and a plan for future heating
# Can estimate the impact of this heating on the temperature at
# a point in the future


class Heating:
    dbname = "heatingplan"

    heat = {}

    heatImpactBlocks = 13

    def Store(self):
        # when saving; discard anything more than a day old
        with shelve.open(self.dbname) as db:
            for k in self.heat:
                db[str(k)] = self.heat[k]

    def Load(self):
        with shelve.open(self.dbname) as db:
            for k in db:
                self.heat[int(k)] = db[k]

    def Clone(self):
        newHeating = Heating()
        newHeating.heat = self.heat.copy()
        return newHeating

    def GetPlannedHeating(self, block):
        if block in self.heat:
            return self.heat[block]
        return False

    def PutPlannedHeating(self, block, heatbool):
        self.heat[block] = heatbool

    # what's the tempterature gain in a certin block due to prior
    # heating?
    def ApplyHeatingForBlock(self, block, initialTemp):
        temp = initialTemp

        if self.GetPlannedHeating(block - 18):
            temp = temp + 0.01

        if self.GetPlannedHeating(block - 17):
            temp = temp + 0.01

        if self.GetPlannedHeating(block - 16):
            temp = temp + 0.02

        if self.GetPlannedHeating(block - 15):
            temp = temp + 0.02

        if self.GetPlannedHeating(block - 14):
            temp = temp + 0.03

        if self.GetPlannedHeating(block - 13):
            temp = temp + 0.03

        if self.GetPlannedHeating(block - 12):
            temp = temp + 0.03

        if self.GetPlannedHeating(block - 11):
            temp = temp + 0.03

        if self.GetPlannedHeating(block - 10):
            temp = temp + 0.04

        if self.GetPlannedHeating(block - 9):
            temp = temp + 0.04

        if self.GetPlannedHeating(block - 8):
            temp = temp + 0.04

        if self.GetPlannedHeating(block - 7):
            temp = temp + 0.06

        if self.GetPlannedHeating(block - 6):
            temp = temp + 0.07

        if self.GetPlannedHeating(block - 5):
            temp = temp + 0.08

        if self.GetPlannedHeating(block - 4):
            temp = temp + 0.07

        if self.GetPlannedHeating(block - 3):
            temp = temp + 0.03

        if self.GetPlannedHeating(block - 2):
            temp = temp + 0.01

        return temp
