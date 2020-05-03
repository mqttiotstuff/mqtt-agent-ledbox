

import traceback
import time

black = (0,0,0)

class LedRing:

    def __init__(self, mqtttopic):
        assert mqtttopic != None
        self.mqtttopic = mqtttopic
        self.all_leds = 70
        self.tworing = 25
        self.onering = int(self.tworing/2)
        self.current = self.feed(self.all_leds, black)
        self.post = self.feed(self.all_leds, black)
        self.remanence = 0.8

    def feed(self, nb, color):
        s = ""
        (r,g,b) = color
        for i in range(0,nb):
            s = s + self.toLed(color)
        return s

    def ring(self, h, color):
        prefix = self.feed(h * int(self.onering), black)
        r = self.feed(self.onering, color)
        suffix_size = self.all_leds - int(len(prefix)/3) - int(len(r)/3)
        suffix = ""
        if suffix_size > 0:
            suffix = self.feed(suffix_size, black)
        message = prefix + r + suffix
        # strip result
        return message[0:self.all_leds * 3] 

    # create dots patterns
    def space(self, color, length = 10, shift = 0, space = 10):
        s = ""
        while len(s) < self.all_leds * 3:

            spacel = self.feed(int(space), black)
            r = self.feed(length, color)
            s = self.feed(shift, black) + r + spacel + s

        # strip result
        return s[0:self.all_leds * 3] 


    # create dots patterns
    def dots(self, color, length = 10, shift = 0, space = 10):
        s = ""
        while len(s) < (self.all_leds + length + space) * 2 * 3: 
            spacel = self.feed(int(space), black)
            r = self.feed(length, color)
            s = r + spacel + s
        s = s[ 3 * shift:]

        # strip result
        returned = s[0:self.all_leds * 3] 
        try:
            assert len(returned) == self.all_leds * 3
            return returned
        except AssertionError:
            print(len(returned))

    def fade(self, s, stage = 0.5):
        retvalue = ""
        for c in s:
            n = ord(c)
            n = int(n * stage)
            retvalue += chr(n)
        return retvalue;

    def add(self, s1,s2):
        if s1 is None:
            s1 = self.feed(self.all_leds, black)

        if s2 is None:
            s2 = self.feed(self.all_leds, black)

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
            s += self.toLed(black) if pixel != i else self.toLed(color)
        return s



    def display(self, client, s):
        if not s:
            s = self.current
        self.post = self.add(self.post, s)
        self.current = self.combine(self.current, self.post)
        self.post = self.fade(self.post)
        client.publish(self.mqtttopic, self.current)


    #############################################################################

    # generator
    def clear(self):
        empty =  self.feed(self.all_leds, black) 
        for i in range(0,10):
            yield empty


    # generator
    def movering(self,direction, color):
        try:
            s = ""
            assert color != None
            (f,t,s) = (0,6,1) if direction == 1 else (5,-1,-1)
            current = self.feed(self.all_leds, black)
            for i in range(f,t,s):
                s =self.ring(i,color)
                yield self.combine(current, s)
        except:
            traceback.print_exc()

    # generator
    def flash(self, color):
        buf = self.feed(self.all_leds, color)

        for i in range(0,10):
            yield buf

        buf = self.feed(self.all_leds, black)
        for i in range(0,10):
            yield buf


    # generator
    def wave(self,color):
        # wave
        return self.sequence(self.movering(1, color), \
            self.movering(2, color))

    def dotAnim (self, color, length, space):
        for i in range(0,2*(length + space)):
            yield self.dots(color, length, i, space)

    def toLed(self, color):
        (r,g,b) = color
        s = ""
        s += chr(g) + chr(r) + chr(b)
        return s

    # generator
    def sequence (self, f1,f2):
        if not f1 is None:
            for i in f1:
                yield i
        if not f2 is None:
            for j in f2:
                yield j




    # generator
    def parallel(self, f1,f2):

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
            yield self.add(s, s2)



############################################################"
#generator combiners

def normaliseColor(c, level):
    (c1,c2,c3) = c
    v = (c1 + c2 + c3) / 3.0
    ratio = level * 1.0 / v
    return (min( int(ratio*c1), 255), (min( int(ratio*c2), 255)), (min( int(ratio*c3), 255)))



