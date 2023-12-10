from nest import NestCredentials
from nest import NestThermostat
from nest import create_device


class Nest:
    status = False

    def GetStatus(self):
        return self.status

    def setNestTargetTemp(self, target):
        try:
            creds = NestCredentials()
            nt = NestThermostat(creds)
            results = nt.get(nest_type="devices")
            for dev in results["devices"]:
                dev = create_device(dev)
                print(
                    "{name}\t [MODE: {mode}] is set to {target_temp:.2f}.  Currently: {temp:.2f}".format(
                        **dev._asdict()
                    )
                )

                currentTarget = round(dev.target_temp, 1)
                nt.target_heat = round(target, 1)

                if nt.target_heat != currentTarget:
                    print("Setting new target temperature: " + str(nt.target_heat))
                    result = nt.set_temp(dev)
                    print(result)

            self.status = True

        except Exception as e:
            print(e)
            self.status = False
