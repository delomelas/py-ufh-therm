# About
A RasPi home thermostat script for controlling slow underfloor heating

![Thermostat Screen](images/finished.jpg?raw=true "Thermostat in action")

# Background
I moved into a new house in the the UK - think 1930s brick construction, gas-heated water central heating. No HVAC or cooling, climate that requires heating for 4-5 months of the year.

The house came with wet underfloor heating (that is, underfloor heating that uses a gas boiler to heat water which is pumped under the floor). Pretty soon I realised that the supplied Nest thermostat was ill-equipped to cope with this - there's about a two-hour lag between the heating being switched on and any impact being felt. The Nest would keep heating away until the target temperature was met and then wildly overshoot as the residual heat in the floor would keep heating the house for hours.

After a few months it was clear it wasn't going to "learn" to do any better, and the wild temperature swings made the house very uncomfortable.

With one eye on the heating bills and one on a fun project, I deciede to build a custom thermostat for the house.

# Important Note
Before going too far - note that this is not something I expect other people to be able to pick up and migrate to their own heating system. The code makes a lot of assumptions about the behavior of the heating here. Be inspired to make something better instead :-)

# Planning
## Requirements
* Low-ish power usage - using a low-powered Pi and e-ink screen
* Fail-safe - this project interfaces with the existing Nest thermostat rather than being wired directly into the boiler. This means a) there's a fail-safe - the Nest will take over again should this system fail and b) no need to wire new relays etc into the boiler to control the zone valves.
* Optimising - Should use the minimum of heat to keep the house above the target temperature. Uses a simple algorithm to plan the next 12h heating, taking into account the natural heat-loss of the building and compensating for the outdoor temperature.
* Local-only - no need for remote control or an app - it takes hours to warm up the house, so better to design a system that keeps a temperature constant and comfortable

# Construction
## Hardware
* Raspberry Pi Zero W - because I had a spare one from years ago
* InkyWHAT 4 inch e-ink sceen - a low-power display option to show information - black/white/red only, 400x300 resolution
* BME280 temperature sensor - cheap and just about accurate enough - it attaches nicely into the breakout pins on the InkyWHAT
* 3d-printed case - to make sure it looks like a real thing and not a mess of PCBs and breadboards in the corner of the room

![BME280, InkyWHAT screen an Pi Zero W](images/hardware.jpg?raw=true "All the required hardware")

## Software
Low-quality code beware! Here be dragons, etc.
* main.py - entry point. Designed to run as cron-job once every 15 minutes - collects all data, plans the next 12h of heating, switches on or off the boiler, then exits
* predictor.py - divides the day into 15 minute blocks, predicting the temperature drop for the next 12h. Assume a simple temperature-gradient, so heat loss will be proportional to the difference between inside and outside temp
* optimiser.py - algorithm to plan future heating - adds 15 min blocks of heating one-by one until the predicted target temperatures are met
* outputgen.py - ugliest bit of code here - lays out the status screen and chart which shows past temperature and predicted future temperature
* weather.py - wrapper for obtaining weather forecasts - in this case from OpenMeteo. We request hourly temperature data for the future
* mynest.py - wrapper around nest.py to simplify accessing Nest to override the old thermostat
* nest.conf - not included, contains API keys and bearer tokens for accessing the Google Smart Device management API

## Configuration
* nest.conf - the script expects to find this with details of the Nest API auth keys and bearer tokens
* heating.py - the heating being on causes a curve in heat output for the following three or so hours, so this attempts to encode that curve
* predictor.py - contains a heat-loss function, calibrated to my house
* main.py - contains target temperatures for each day

## Display
I wanted something functional yet elegant - spent a bit of time laying out the information on paper first to decide what goes where on the display. Had thoughts about including extra information - more detailed weather forecast? pull in the cost from the Smert Meter? Maybe later, but better to leave it relatively uncluttered for now.
The display indicates:
* Current indoor temperature
* Current outdoor temperature
* Time the update last ran (because it's an e-ink display, this seemed to be the best way to check it was working!)
* Chart which shows
  * Solid line in the past; detected temperature
  * Dotted line in the futre; predicted temperature
  * Red line; target temperature
  * Red Bars - times when the heating is on
* Status area in the bottom left, which confirms successful link with the weather API, Nest API and Sensors.
* On/Off indicator bottom-middle, at-a-glance view of if the boiler is on or off at the moment
* Total heating time over the last 24h, so I can marvel in how efficient it is

![Thermostat chart](images/display.png?raw=true "Detail view of the output screen")

## The finished item
![Case open](images/insides.jpg?raw=true "Another view of the case")

* Seems to be working well so far
* It updates once every fifteen minutes - updating the display and setting the heating either on or off.
* Might need a bit more config and calibration to get the heat-curves just right for heat-loss and input from the heating system. I wonder if accounting for solar gains and wind-chill will help too?

# Credits and acknowledgements

## Fonts
* https://www.dafont.com/chunky-dunk.font
* https://www.dafont.com/quicksand.font

## Nest script
* API script from https://github.com/kwoodson/thermostat
* Help and advice from https://github.com/axlan/python-nest

## Case
* Design by DigitalUrban https://www.thingiverse.com/thing:4036382

## Weather Forecast
* https://open-meteo.com/

