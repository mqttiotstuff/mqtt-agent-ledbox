
#
# MQTT agent translating meaning into ledbox animations
#



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
import led_ring

import time

import threading
import queue

import expression

config = RawConfigParser()

LEDBBOX_TOPIC="home/agents/ledbox/run"

MESSAGE_BASE_TOPIC="home/agents/informations"
MESSAGE_TOPIC=MESSAGE_BASE_TOPIC + "/message"
WATCHDOG_TOPIC=MESSAGE_BASE_TOPIC + "/watchdog"

client2 = None



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    try:
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.

        client.subscribe(MESSAGE_TOPIC)
        print("End of registration")
    except:
        traceback.print_exc()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global client2
    global monitoring_lasttime
    try:
       # print str(msg)
       # print("message " + str(msg))


       if msg.topic.startswith(MESSAGE_TOPIC):
           try:
               message = msg.payload.decode('utf-8')
               s = informationMapping(message)
               if s is not None and s != "":
                   client2.publish(LEDBBOX_TOPIC, "sequence(" + s + ",clear())")
           except:
               traceback.print_exc()

    except:
        traceback.print_exc()


def informationMapping(message):
    words = { "internet" : "fg(fadd(fpixel(10,blue),fpixel(9,blue), fpixel(21,red), fpixel(32,green),  fpixel(33,green)))", 
             "site": "fg(fadd(  fpixel(20,blue), fpixel(21,blue), fpixel(31,blue), fpixel(32,blue), fpixel(33,blue), fpixel(43,blue), fpixel(44,blue) ))",
            "quentin": "fg(fpixel(11,green))",
            "yann": "fg(fadd(fpixel(11,green), fpixel(22,green)))",
            "connecte": "fg(fadd(fpixel(10,blue),fpixel(21,blue), fpixel(32,blue)))",
            "nop": "clear()",

            "day": "fg(fadd(fpixel(33,blue),fpixel(31,blue),fpixel(35,blue) ))",
            "night": "fg(fadd(fpixel(33,uiyellow),fpixel(31,uiyellow),fpixel(35,uiyellow) ))",

              "down":"dotanim(red,1,4)",
              "up":"movering(0,blue)" }
    s = ""
    for i in message.split():
        if i in words:
            if s == "":
                s = words[i]
            else:
                s = "sequence(" + s + "," + words[i] + ")"
        else:
            print("word " + i + " not found")

    return s




conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
    raise Exception("config file " + conffile + " not found")

config.read(conffile)


client = mqtt.Client(clean_session=True, userdata=None, protocol=mqtt.MQTTv311)

client.on_connect = on_connect
client.on_message = on_message


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client.username_pw_set(username,password)
client.connect(mqttbroker, 1883, 5)
client.will_set("home/agents/informations/lwt", 
        payload="disconnected", qos=0, retain=False)


client2 = mqtt.Client(clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
client2.username_pw_set(username,password)
client2.connect(mqttbroker, 1883, 5)
client2.will_set("home/agents/informations/lwt", payload="disconnected", qos=0, retain=False)

client2.loop_start()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_start()

while True:
    try:
        time.sleep(2)
        client.publish(MESSAGE_BASE_TOPIC + "/healthcheck", "1")
    except:
        traceback.print_exc()



