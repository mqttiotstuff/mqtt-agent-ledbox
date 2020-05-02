

import traceback
import time

class LedRing:

    def __init__(self, mqtttopic):
        assert mqtttopic != None
        self.mqtttopic = mqtttopic
        self.all_leds = 70
        self.tworing = 25
        self.onering = int(self.tworing/2)
        self.current = self.feed(self.all_leds, (0,0,0))
        self.post = self.feed(self.all_leds, (0,0,0))
        self.remanence = 0.8

    def feed(self, nb, color):
        s = ""
        (r,g,b) = color
        for i in range(0,nb):
            s = s + self.toLed(color)
        return s

    def ring(self, h, color):
        prefix = self.feed(h * int(self.onering), (0,0,0))
        r = self.feed(self.onering, color)
        suffix_size = self.all_leds - int(len(prefix)/3) - int(len(r)/3)
        suffix = ""
        if suffix_size > 0:
            suffix = self.feed(suffix_size, (0,0,0))
        message = prefix + r + suffix
        return message[0:self.all_leds * 3] 

    def display(self, client, s):
        if not s:
            s = self.current
        self.post = self.add(self.post, s)
        self.current = self.combine(self.current, self.post)
        self.post = self.fade(self.post)
        client.publish(self.mqtttopic, self.current)

    def fade(self, s, stage = 0.5):
        retvalue = ""
        for c in s:
            n = ord(c)
            n = int(n * stage)
            retvalue += chr(n)
        return retvalue;

    def add(self, s1,s2):
        if s1 is None:
            s1 = self.feed(self.all_leds, (0,0,0))

        if s2 is None:
            s2 = self.feed(self.all_leds, (0,0,0))

        retvalue = ""
        assert len(s1) == len (s2)
        for i in range(0,len(s1)):
            v = 0
            v = ord(s1[i]) + ord(s2[i])
            if v > 128:
                v = 128
            retvalue += chr(v)
        return retvalue

    def combine(self, s1,s2):
        return self.add(self.fade(s1),self.fade(s2))

    def pixel(self, pixel, color):
        s = ""
        for i in range(0, self.all_leds):
            s += self.toLed((0,0,0)) if pixel != i else self.toLed(color)
        return s

    #############################################################################

    # generator
    def clear(self, client):
        empty =  self.feed(self.all_leds, (0,0,0)) 
        for i in range(0,10):
            yield empty


    # generator
    def movering(self, client2, direction, color):
        try:
            s = ""
            assert color != None
            (f,t,s) = (0,6,1) if direction == 1 else (5,-1,-1)
            current = self.feed(self.all_leds, (0,0,0))
            for i in range(f,t,s):
                s =self.ring(i,color)
                yield self.combine(current, s)
        except:
            traceback.print_exc()

    def toLed(self, color):
        (g,r,b) = color
        s = ""
        s += chr(g) + chr(r) + chr(b)
        return s

