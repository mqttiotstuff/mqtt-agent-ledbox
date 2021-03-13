
import paho.mqtt.client as mqtt
import random
import time
import traceback
import re

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


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")


client2 = mqtt.Client(clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
client2.username_pw_set(username,password)
client2.connect(mqttbroker, 1883, 5)
client2.will_set("home/agents/ledbox/lwt", payload="disconnected", qos=0, retain=False)


ledring = LedRing("home/esp13/actuators/ledstrip")


def on_connect(client, userdata, flags, rc):
    try:
        print("connected")
        # flash

        buf = ledring.feed(ledring.all_leds, (255,0,0))
        for i in range(0,10):
            ledring.display(client2,buf)
            time.sleep(0.2)

        buf = ledring.feed(ledring.all_leds, (0,0,0))
        for i in range(0,10):
            ledring.display(client2,buf)
            time.sleep(0.2)

    except:
        traceback.print_exc()


client2.on_connect = on_connect

client2.loop_forever()

