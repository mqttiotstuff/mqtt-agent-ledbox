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


def get_config_item(section, name, default):
    """
    Gets an item from the config file, setting the default value if not found.
    """
    try:
        value = config.get(section, name)
    except:
        value = default
    return value


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
color = red

ledring.movering(client2, 1, color, waittime=0.1)
ledring.movering(client2, 2, color, waittime=0.1)

for i in range(0, ledring.all_leds):
    ledring.display(client2, ledring.pixel(i,color))
    time.sleep(0.1)

ledring.clear(client2)


