
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


config = RawConfigParser()

ALERTE_TOPIC="home/agents/ledbox/alerte"
TEST_TOPIC="home/agents/ledbox/test"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(PERSO_TOPIC)
    client.subscribe(TEST_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

   # print str(msg)

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


   if msg.topic == PERSO_TOPIC:
       try:
           # c = random.randint(0,16*16)
           nb = int(msg.payload)
           print("display " + str(nb))

           time.sleep(0.2)
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

