
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

ALERTE_TOPIC="home/agents/ledbox/alerte"
BLUEWAVE_TOPIC="home/agents/ledbox/bluewave"
TEST_TOPIC="home/agents/ledbox/test"
INTERRUPTOR="home/esp13/sensors/interrupt"

ledring = LedRing("home/esp13/actuators/ledstrip")

generatorQueue = queue.Queue()

client2 = None

# generator
def wave(client, color):
    # wave
    return sequence(ledring.movering(client2, 1, color), \
    ledring.movering(client2, 2, color))

# generator
def sequence (f1,f2):
    if not f1 is None:
        for i in f1:
            yield i
    if not f2 is None:
        for j in f2:
            yield j

# generator
def combine(f1,f2):

    while not (f1 is None and f2 is None):
        s = None
        if f1 != None:
            try:
                s = next(f1)
            except StopIteration:
                f1 = None
        s2 = None
        if f2 != None:
            try:
                s2 = next(f2)
            except StopIteration:
                f2 = None
        yield ledring.add(s, s2)


def normaliseColor(c, level):
    (c1,c2,c3) = c
    v = (c1 + c2 + c3) / 3.0
    ratio = level * 1.0 / v
    return (min( int(ratio*c1), 255), (min( int(ratio*c2), 255)), (min( int(ratio*c3), 255)))



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    try:
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(ALERTE_TOPIC)
        client.subscribe(BLUEWAVE_TOPIC)
        client.subscribe(TEST_TOPIC)
        client.subscribe(INTERRUPTOR + "1")
        client.subscribe(INTERRUPTOR + "2")
        client.subscribe(INTERRUPTOR + "3")
        client.subscribe(INTERRUPTOR + "4")
        print("End of registration")
    except:
        traceback.print_exc()

level = 50
red = normaliseColor((0,100,0),level)
green = normaliseColor((100,0,0),level)
blue = normaliseColor((0,0,100),level)

pink = normaliseColor((192,255,203),level)
purple = normaliseColor((0,148,211),level)


def run(generator):
    assert generator != None
    print("add generator")
    generatorQueue.put(generator) 

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global client2
    try:
       # print str(msg)
       print("message " + str(msg))
       if msg.topic.startswith(INTERRUPTOR):
           try:
               print(msg.payload)
               if msg.payload == b'1':
                   color = blue
                   if msg.topic == INTERRUPTOR + "1":
                       run(sequence(wave(client2, blue), ledring.clear(client2)))
                   if msg.topic == INTERRUPTOR + "2":
                       run(sequence(wave(client2, green), ledring.clear(client2)))
                   if msg.topic == INTERRUPTOR + "3":
                       run(sequence(wave(client2, purple), ledring.clear(client2)))
                   if msg.topic == INTERRUPTOR + "4":
                       run(sequence(wave(client2, pink), ledring.clear(client2)))
                   return;

           except:
               traceback.print_exc()

#       if msg.topic == BLUEWAVE_TOPIC:
#           try:
#               run(wave(client2, blue))
#               run(ledring.clear(client2))
#               run(ledring.clear(client2))
#           except:
#               traceback.print_exc()


       if msg.topic == ALERTE_TOPIC:
           try:
               print(msg.payload)
               s = msg.payload.decode("utf-8")
               print(s)
               c = re.compile("^([0-9]+),([0-9]+),([0-9]+)$")
               m = c.match(s)
               if not m is None:
                   color = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                   print(color)
                   run(wave(client2, color))
               else:
                   run(wave(client2, red))

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
                    print("get iterator")
                    assert incomingGenerator != None
                    currentGenerator = combine(currentGenerator, incomingGenerator);
                    print(currentGenerator)
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

