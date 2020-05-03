
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
import re

from configparser import ConfigParser
from configparser import RawConfigParser
import os.path

import unicodedata

from led_ring import *


import threading
import queue

config = RawConfigParser()

ALERTE_TOPIC="home/agents/ledbox/alert"
WAVE_TOPIC="home/agents/ledbox/wave"
DOTS_TOPIC="home/agents/ledbox/dots"
DOTS_TOPIC2="home/agents/ledbox/dots2"
TEST_TOPIC="home/agents/ledbox/test"
INTERRUPTOR="home/esp13/sensors/interrupt"

ledring = LedRing("home/esp13/actuators/ledstrip")

generatorQueue = queue.Queue()

client2 = None



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    try:
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(ALERTE_TOPIC)
        client.subscribe(WAVE_TOPIC)
        client.subscribe(DOTS_TOPIC)
        client.subscribe(DOTS_TOPIC2)
        client.subscribe(TEST_TOPIC)
        client.subscribe(INTERRUPTOR + "1")
        client.subscribe(INTERRUPTOR + "2")
        client.subscribe(INTERRUPTOR + "3")
        client.subscribe(INTERRUPTOR + "4")
        print("End of registration")
    except:
        traceback.print_exc()

level = 50
red = normaliseColor((100,0,0),level)
green = normaliseColor((0,100,0),level)
blue = normaliseColor((0,0,100),level)

pink = normaliseColor((255,192,203),level)
purple = normaliseColor((148,0,211),level)


def run(generator):
    assert generator != None
    generatorQueue.put(generator) 

def decodeColor(payload):
    try:
        # R,G,B
        s = payload.decode("utf-8")
        c = re.compile("^([0-9]+),([0-9]+),([0-9]+)$")
        m = c.match(s)
        if not m is None:
            color = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return color
        return None # not decoded
    except:
        traceback.print_exc()
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global client2
    try:
       # print str(msg)
       # print("message " + str(msg))
       if msg.topic.startswith(INTERRUPTOR):
           try:
               # print(msg.payload)
               if msg.payload == b'1':
                   color = blue
                   if msg.topic == INTERRUPTOR + "1":
                       run(ledring.sequence(ledring.wave(blue), ledring.clear()))
                   if msg.topic == INTERRUPTOR + "2":
                       run(ledring.sequence(ledring.wave(green), ledring.clear()))
                   if msg.topic == INTERRUPTOR + "3":
                       run(ledring.sequence(ledring.wave(purple), ledring.clear()))
                   if msg.topic == INTERRUPTOR + "4":
                       run(ledring.sequence(ledring.wave(pink), ledring.clear()))
                   return;

           except:
               traceback.print_exc()

       if msg.topic == ALERTE_TOPIC:
           try:
               color = decodeColor(msg.payload)
               if not color is None:
                   run(ledring.flash(color))
               else:
                   # if not parsable, put red
                   run(ledring.flash(red))

           except:
               traceback.print_exc()

       if msg.topic == DOTS_TOPIC:
           try:
               color = decodeColor(msg.payload)
               if not color is None:
                   run(ledring.sequence(ledring.dotAnim(color, 1, 4), ledring.clear()))
               else:
                   print("the color does not correspond to expected format : r,v,b")
           except:
               traceback.print_exc()

       if msg.topic == DOTS_TOPIC2:
           try:
               color = decodeColor(msg.payload)
               if not color is None:
                   run(ledring.sequence(ledring.dotAnim(color, 7,15), ledring.clear()))
               else:
                   print("the color does not correspond to expected format : r,v,b")
           except:
               traceback.print_exc()



       if msg.topic == WAVE_TOPIC:
           try:
               color = decodeColor(msg.payload)
               if not color is None:
                   run(ledring.wave(color))
               else:
                   print("the color does not correspond to expected format : r,v,b")

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

               # client2.publish("home/esp13/actuators/led8", s) 
               print("done")
           except:
               traceback.print_exc()

    except:
        traceback.print_exc()


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
client.will_set("home/agents/ledbox/lwt", payload="disconnected", qos=0, retain=False)


class MainThread(threading.Thread):
    def run(self):
        global client2
        global username
        global password
        global mqttbroker
        count = 5
        client2 = mqtt.Client(clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        client2.username_pw_set(username,password)
        client2.connect(mqttbroker, 1883, 5)
        client2.will_set("home/agents/ledbox/lwt", payload="disconnected", qos=0, retain=False)

        client2.loop_start()
        print("init done")
        currentGenerator = None
        while True:
            try:
                s = None
                if currentGenerator != None:
                    try:
                        s = next(currentGenerator)
                        assert len(s) == ledring.all_leds * 3
                    except StopIteration:
                        currentGenerator = None

                if s is not None:
                    count = 5

                if s is None:
                    count = count - 1
                    if count > 0:
                        s = ledring.feed(ledring.all_leds, (0,0,0))

                if s is not None:
                    ledring.display(client2,s)

                try:
                    # pump generator and combine with previous if exists
                    incomingGenerator = generatorQueue.get(timeout=0.005)
                    assert incomingGenerator != None
                    currentGenerator = ledring.parallel(currentGenerator, incomingGenerator);
                except queue.Empty:
                    pass
            except:
                traceback.print_exc()
            time.sleep(0.1)


mainThread = MainThread()
mainThread.start()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()

