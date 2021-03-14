#
# MQTT agent to manage a LED ring object
#
#


import paho.mqtt.client as mqtt
import random
import time
import traceback

import functools

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
        time.sleep(0.2)

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
        last = None
        for i in range(f, t, s):
            try:
                color = next(colorgenerator)
                last = color
            except StopIteration:
                pass
            if last is not None:
                s = ledring.ring(i, last)
                yield ledring.combine(current, s)
    except:
        traceback.print_exc()


l = ledring.linear_color(uiblue, uigreen, 5)

l2 = ledring.rainbow_color(size=10)
l22 = ledring.rainbow_color(size=2)

l3 = ledring.fixed_color(uiblue)

#s = ledring.switch_color( colors=[uiindigo,uipink]   )
## colors from https://materialuicolors.co/
#uipink = (233, 30, 99)
#uired = (244, 67, 54)
#uiblue = (33, 150, 243)
#uilightblue = (3, 169, 244)
#uipurple = (156, 39, 176)
#uideeppurple = (103, 58, 183)
#uiindigo = (63, 81, 181)
#uicyan = (0, 188, 212)
#uiteal = (0, 150, 136)
#uigreen = (76, 175, 80)
#uilightgreen = (139, 195, 74)
#uilime = (205, 220, 57)
#uiyellow = (255, 235, 59)
#uiamber = (255, 193, 7)
#uiorange = (255, 152, 0)
#uideeporange = (255, 87, 34)
#uibrown = (121, 85, 72)
#uigrey = (158, 158, 158)
#uibluegrey = (96, 125, 139)
#


s = ledring.switch_color( colors=[uiblue,uired], times=2   )

# display(ledring.dotAnimCg(s,7,3))

# sequence = ledring.parallel(
#                 ledring.colored_square(ledring.fixed_color(blue), nbpatterns=3, squaresize=1),
#                 ledring.colored_square(ledring.fixed_color(red), nbpatterns=3, squaresize=1, shift = 2)
#     )
# display(sequence)
# 

# ledring.display(client2, ledring.ring(4, blue))

# display(ledring.fg(ledring.ring(2,blue)))
# display(ledring.fg(ledring.add(ledring.ring(0,blue), ledring.ring(4,red))))
# 
# display(ledring.fg(
#     ledring.add(
#     ledring.add(
#         ledring.fill_patterns(red, space=ledring.onering/3),
#         ledring.fill_patterns(blue, space=ledring.onering/3,shift =1)
#         ),
#         ledring.fill_patterns(green, space=ledring.onering/3, shift=2),
#     )
# ))
# 

display(ledring.parallel(ledring.rain(red),ledring.shift(ledring.rain(green),4),ledring.rain(blue)))
# display(ledring.sequence(ledring.flash(red),ledring.flash(green)))


# display(ledring.fg(ledring.dots(red, length=ledring.all_leds, shift=0, space=2)))


#display(ledring.sequence(movering(direction=1,colorgenerator=l2),movering(direction=0,colorgenerator=l2)))

# display(movering(direction=1,colorgenerator=s))

# display(wave_and_dots(uipink))

# display(ledring.parallel(movering(1,l2), ledring.shift(movering(0,l3), 4)))


# ledring.display(client2, ledring.square_pattern(green))
#
#display(ledring.parallel(
#            ledring.sequence(
#                ledring.colored_square(ledring.fixed_color(blue), nbpatterns=6, squaresize=1),
#                ledring.colored_square(ledring.fixed_color(white), nbpatterns=4, squaresize=2),
#            ),
#    ledring.parallel(
#            ledring.rain(red),
#            ledring.rain(blue),2)
#        ))



#
# for i in range(0,1):
#     display(ledring.parallel(
#         ledring.slow(ledring.rain(uipink)),
#         ledring.sequence(
#             ledring.fast(ledring.colored_square(ledring.fixed_color(uilightblue),
#                                                 nbpatterns=3, squaresize=3)),
#             ledring.fast(ledring.colored_square(ledring.fixed_color(uigreen),
#                                               nbpatterns=2, squaresize=3)),
#         ), 15))

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
