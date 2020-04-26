#
# MQTT agent to manage a LED ring object
#
#



import paho.mqtt.client as mqtt
import random
import time
import traceback

from configparser import ConfigParser
from configparser import RawConfigParser
import os.path

import unicodedata
from led_ring import *

config = RawConfigParser()

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
    raise Exception("config file " + conffile + " not found")

config.read(conffile)

# colors are define by the tuple (Green, red, blue)
#####################################################################
# moving rings

ledring = LedRing("home/esp13/actuators/ledstrip")

client2 = mqtt.Client()


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client2.username_pw_set(username,password)
client2.connect(mqttbroker, 1883, 5)

red = (0,100,0)
green = (100,0,0)
blue = (0,0,100)
color = red

def wave(client, color):
    # wave
    ledring.movering(client, 1, color, waittime=0.1)
    ledring.movering(client, 2, color, waittime=0.1)

wave(client2,red)
wave(client2,green)
wave(client2,blue)


# moving anneling
for i in range(0, ledring.all_leds):
    ledring.display(client2, ledring.pixel(i,color))
    time.sleep(0.1)

for i in range(0, ledring.all_leds):
    randomColor = (g,r,b) = (random.randint(0,80),random.randint(0,80),random.randint(0,80))
    ledring.display(client2, ledring.pixel(i,randomColor))
    ledring.display(client2, ledring.pixel(ledring.all_leds - i,randomColor))
    time.sleep(0.05)



ledring.clear(client2)


