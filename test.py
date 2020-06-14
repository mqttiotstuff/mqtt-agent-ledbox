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

username = config.get("agents", "username")
password = config.get("agents", "password")
mqttbroker = config.get("agents", "mqttbroker")

client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 5)

green = (0, 100, 0)
red = (100, 0, 0)
blue = (0, 0, 100)
white = (100, 100, 100)
color = red

# colors from https://materialuicolors.co/
uipink = (233, 30, 99)
uired = (244, 67, 54)
uiblue = (33, 150, 243)
uilightblue = (3, 169, 244)
uipurple = (156, 39, 176)
uideeppurple = (103, 58, 183)
uiindigo = (63, 81, 181)
uicyan = (0, 188, 212)
uiteal = (0, 150, 136)
uigreen = (76, 175, 80)
uilightgreen = (139, 195, 74)
uilime = (205, 220, 57)
uiyellow = (255, 235, 59)
uiamber = (255, 193, 7)
uiorange = (255, 152, 0)
uideeporange = (255, 87, 34)
uibrown = (121, 85, 72)
uigrey = (158, 158, 158)
uibluegrey = (96, 125, 139)

def display(generator):
    # display the generator
    for e in generator:
        ledring.display(client2, e)
        time.sleep(0.1)

    for e in ledring.clear():
        ledring.display(client2, e)
        time.sleep(0.2)


def wave_and_dots(color):
    # wave
    generator = ledring.sequence(
        ledring.sequence(ledring.movering(1, color),
                         ledring.movering(2, color)),
        ledring.dotAnim(color, 3, 6))

    return generator



def movering(direction, colorgenerator):
    try:
        s = ""
        assert colorgenerator is not None
        (f, t, s) = (0, 6, 1) if direction == 1 else (5, -1, -1)
        current = ledring.feed(ledring.all_leds, black)
        for i in range(f, t, s):

            try:
                color = next(colorgenerator)
            except StopIteration:
                pass
            s = ledring.ring(i, color)
            yield ledring.combine(current, s)
    except:
        traceback.print_exc()


l = ledring.linear_color(uiblue, uigreen, 5)

l2 = ledring.rainbow_color(size=2)
l22 = ledring.rainbow_color(size=2)

l3 = ledring.fixed_color(uiblue)

# display(ledring.sequence(movering(1,l2), movering(0,l2)))

# display(ledring.parallel(movering(1,l2), movering(0,l3), 4))


# ledring.display(client2, ledring.square_pattern(green))

# display(ledring.parallel(
#            ledring.fast(ledring.colored_square(ledring.fixed_color(blue))),
#            ledring.rain(blue), 10))

display(ledring.parallel(
    ledring.slow(ledring.rain(uipink)),
    ledring.sequence(
        ledring.fast(ledring.colored_square(ledring.fixed_color(uilightblue),
                                            nbpatterns=3, squaresize=2)),
        ledring.fast(ledring.colored_square(ledring.fixed_color(uigreen),
                                            nbpatterns=6, squaresize=1)),
    ), 15))

# display(ledring.sequence(movering(1,l2), movering(1,l2)))


# display(ledring.sequence(movering(1,l3), movering(1,l3)))


# display(wave_and_dots(red))
# display(randomDotColor())

# display(ledring.flash(white))

# display(ledring.dotAnim(red,3,10))
# display(ledring.dotAnim(red,10,10))

# display(ledring.fast(ledring.flash(red)))
# display(ledring.fast(ledring.dotAnim(red,10,10)))

# wave(client2,green)
# wave(client2,blue)


# moving anneling
# for i in range(0, ledring.all_leds):
#    ledring.display(client2, ledring.pixel(i,blue))
#    time.sleep(0.1)

# for i in range(0, ledring.all_leds):
#    randomColor = (g,r,b) = (random.randint(0,80),random.randint(0,80),random.randint(0,80))
#    ledring.display(client2, ledring.pixel(i,randomColor))
#    ledring.display(client2, ledring.pixel(ledring.all_leds - i,randomColor))
#    time.sleep(0.05)

display(ledring.clear())
