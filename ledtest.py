
#
# MQTT agent to manage a LED screen
#
#
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

ALERTE_TOPIC="home/agents/ledbox/alerte"
TEST_TOPIC="home/agents/ledbox/test"
INTERRUPTOR="home/esp13/sensors/interrupt1"

ledring = LedRing("home/esp13/actuators/ledstrip")

def wave(client, color):
    # wave
    ledring.movering(client, 1, color, waittime=0.1)
    ledring.movering(client, 2, color, waittime=0.1)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    try:
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(ALERTE_TOPIC)
        client.subscribe(TEST_TOPIC)
        client.subscribe(INTERRUPTOR)
        print("End of registration")
    except:
        traceback.print_exc()

red = (0,100,0)
green = (100,0,0)
blue = (0,0,100)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
       # print str(msg)
       print("message " + str(msg))
       if msg.topic == INTERRUPTOR:
           try:
               print(msg.payload)
               if msg.payload == b'1':
                   print("wave red")
                   wave(client2, red)
                   ledring.clear(client2)
                   ledring.clear(client2)


           except:
               traceback.print_exc()


       if msg.topic == TEST_TOPIC:
           try:
               c = random.randint(0,16*16)
               s = ""
               for j in range(0,8):
                   for i in range(0,8):
                       c = (j * 8 + i) % 10
                       if (c == 0):
                           s = s + (chr(0) + chr(0) + chr(0))
                       else:
                           s = s + (chr(127) + chr(127) + chr(127))
               print(len(s))

               client2.publish("home/esp13/actuators/led8", s) 
               print("done")
               time.sleep(0.2)
           except:
               traceback.print_exc()

    except:
        traceback.print_exc()


conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
    raise Exception("config file " + conffile + " not found")

config.read(conffile)


client = mqtt.Client()
client2 = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client.username_pw_set(username,password)
client.connect(mqttbroker, 1883, 5)

client2.username_pw_set(username,password)
client2.connect(mqttbroker, 1883, 5)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()
client.loop_forever()

