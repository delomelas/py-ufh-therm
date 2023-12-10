#!/usr/bin/env python

# forked from https://github.com/kwoodson/thermostat
from collections import namedtuple
import os
import json
import requests


base_nest_url = "https://smartdevicemanagement.googleapis.com/v1/"

Thermostat = namedtuple("Thermostat", ["name", "temp", "target_temp", "mode", "id"])


class NestCredentialsException(Exception):
    pass


class NestCredentials:
    """
    class to read credentials
    """

    def __init__(self, path="nest.conf"):
        self.path = path

        self.project_id = None
        self.client_id = None
        self.client_secret = None
        self.refresh_token = None
        self.load_credentials()

    def load_credentials(self):
        path = os.path.expanduser(self.path)
        if not os.path.exists(path):
            print("The credentials file is missing.")
            raise NestCredentialsException("CredentialFileMissing")

        data = None

        with open(path) as fd:
            data = json.loads(fd.read())

        if not data:
            raise NestCredentialsException("Error loading credentials file.")

        self.refresh_token = data["refresh_token"]
        self.client_secret = data["client_secret"]
        self.project_id = data["project_id"]
        self.client_id = data["client_id"]


class NestThermostat:
    """
    simple class to control a nest thermostat using google's APIs
    """

    def __init__(self, creds, target_cool=20, target_heat=20):
        self.target_cool = target_cool
        self.target_heat = target_heat
        self.creds = creds
        self.access_token = self._refresh_access_token()

    def _refresh_access_token(self):
        payload = {
            "client_id": self.creds.client_id,
            "client_secret": self.creds.client_secret,
            "refresh_token": self.creds.refresh_token,
            "grant_type": "refresh_token",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        rval = requests.post(
            "https://oauth2.googleapis.com/token", data=payload, headers=headers, timeout = 10
        )
        if rval.status_code != 200:
            raise f"Error refreshing token: {rval.status_code} {rval.reason}"
        return rval.json()["access_token"]

    def set_temp(self, dev):
        """
        set target temperature of thermostat
        POST /enterprises/project-id/devices/device-id:executeCommand
        {
          "command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
          "params" : {
            "heatCelsius" : 22.0
          }
        }
        """
        if dev.mode == "COOL":
            mode = "coolCelsius"
            command = "SetCool"
            temp = self.target_cool
        else:
            mode = "heatCelsius"
            command = "SetHeat"
            temp = self.target_heat

        data = {
            "params": {
                mode: temp,
            },
            "command": f"sdm.devices.commands.ThermostatTemperatureSetpoint.{command}",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        url = base_nest_url + dev.id
        url += ":executeCommand"
        rval = requests.post(url, data=json.dumps(data), headers=headers, timeout = 10)
        print(rval)
        # if rval.status == 200:
        #    print(f"Success: Temparature set to {TempUtils.c_to_f(temp)}")
        # if rval.status_code != 200:
        #    raise f"Error refreshing token: {rval.status_code} {rval.reason}"
        return rval.json()

    def get(self, nest_type="structures"):
        """
        get method to fetch structures or devices
        """
        url = base_nest_url + f"enterprises/{self.creds.project_id}/{nest_type}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        rval = requests.get(url, headers=headers, timeout = 10)
        # import pdb; pdb.set_trace()
        return rval.json()


def create_device(dev):
    """
    create an easier device object
    """
    dname = dev["parentRelations"][0]["displayName"]
    temp = dev["traits"]["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"]
    goal_temp = dev["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"][
        "heatCelsius"
    ]
    mode = dev["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
    did = dev["name"]
    return Thermostat(dname, temp=temp, target_temp=goal_temp, mode=mode, id=did)
