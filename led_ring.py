import traceback
import time
import random
import functools

black = (0, 0, 0)

green = (0, 100, 0)
red = (100, 0, 0)
blue = (0, 0, 100)
white = (255, 255, 255)

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



class LedRing:

    def __init__(self, mqtttopic):
        assert mqtttopic != None
        self.mqtttopic = mqtttopic
        self.all_leds = 70
        self.tworing = 25
        self.onering = int(self.tworing / 2)
        self.current = self.feed(self.all_leds, black)
        self.post = self.feed(self.all_leds, black)
        self.remanence = 0.8

    def toLed(self, color):
        """
            convert color (tuple), into led screen command string
        """
        (r, g, b) = color
        s = ""
        s += chr(g) + chr(r) + chr(b)
        return s

    def feed(self, nb, color):
        s = ""
        (r, g, b) = color
        for i in range(0, nb):
            s = s + self.toLed(color)
        return s

    def ring(self, h, color):
        prefix = self.feed(h * int(self.onering), black)
        r = self.feed(self.onering, color)
        suffix_size = self.all_leds - int(len(prefix) / 3) - int(len(r) / 3)
        suffix = ""
        if suffix_size > 0:
            suffix = self.feed(suffix_size, black)
        message = prefix + r + suffix
        # strip result
        return message[0:self.all_leds * 3]

        # create dots patterns frame

    def space(self, color, length=10, shift=0, space=10):
        s = ""
        while len(s) < self.all_leds * 3:
            spacel = self.feed(int(space), black)
            r = self.feed(length, color)
            s = self.feed(shift, black) + r + spacel + s

        # strip result
        return s[0:self.all_leds * 3]

        # create dots patterns

    def dots(self, color, length=10, shift=0, space=10):
        s = ""
        while len(s) < (self.all_leds + length + space) * 2 * 3:
            spacel = self.feed(int(space), black)
            r = self.feed(length, color)
            s = r + spacel + s
        s = s[3 * shift:]

        # strip result
        returned = s[0:self.all_leds * 3]
        try:
            assert len(returned) == self.all_leds * 3
            return returned
        except AssertionError:
            print(len(returned))

    def fade(self, led_frame, stage=0.5):
        """
        change the brightness level of a led frame
        :param led_frame:
        :param stage: the factor, must be < 1
        :return: the modified led_frame
        """
        retvalue = ""
        for c in led_frame:
            n = ord(c)
            n = int(n * stage)
            retvalue += chr(n)
        return retvalue;

    def add(self, led_frame1, led_frame2):
        if led_frame1 is None:
            led_frame1 = self.feed(self.all_leds, black)

        if led_frame2 is None:
            led_frame2 = self.feed(self.all_leds, black)

        retvalue = ""
        assert len(led_frame1) == len(led_frame2)
        for i in range(0, len(led_frame1)):
            v = 0
            v = ord(led_frame1[i]) + ord(led_frame2[i])
            if v > 128:
                v = 128
            retvalue += chr(v)
        return retvalue

    def combine(self, led_frame1, led_frame2):
        """
        mix two led frame
        :param led_frame1:
        :param led_frame2:
        :return:
        """
        return self.add(self.fade(led_frame1), self.fade(led_frame2))

    def pixel(self, pixel, color):
        """
        create a one pixel frame
        :param pixel: the pixel number
        :param color: the pixel color
        :return:
        """
        s = ""
        for i in range(0, self.all_leds):
            s += self.toLed(black) if pixel != i else self.toLed(color)
        return s

    def display(self, client, led_frame):
        """
        This function send the current frame s to client "client"

        :param client:
        :param led_frame: the led frame to display
        :return:
        """
        if not led_frame:
            led_frame = self.current
        self.post = self.add(self.post, led_frame)
        self.current = self.combine(self.current, self.post)
        self.post = self.fade(self.post)
        client.publish(self.mqtttopic, self.current)

    #############################################################################
    # patterns led frames

    def square_pattern(self, color, nbpatterns=2, square_size=3, shift=0):
        s2 = None
        for i in range(0, nbpatterns):
            setpOffset = int(self.onering / nbpatterns) * i + shift
            square = self.add(
                self.add(self.space(color, square_size, 20 + setpOffset, 50),
                         self.space(color, square_size, 20 + self.onering + setpOffset, 50)
                         ), 
                    self.space(color, square_size, 20 + 2 * self.onering + setpOffset, 50))

            if s2 is None:
                s2 = square
            else:
                s2 = self.add(s2, square)
        return s2

    #############################################################################
    # colors generators

    def linear_color(self, fromcolor, tocolor, size=10):
        """
        create a linear color generator fromcolor tocolor, with a size number of frames
        :param fromcolor:
        :param tocolor:
        :param size:
        :return:
        """
        (a, b, c) = fromcolor
        (a2, b2, c2) = tocolor

        for i in range(0, size):
            yield (int((a2 - a) / size * i + a),
                   int((b2 - b) / size * i + b),
                   int((c2 - c) / size * i + c))

    def fixed_color(self, color, framesize=5):
        """
        create a fixed color generator
        :param color:
        :return:
        """
        for i in range(0, framesize):
            yield color

    def rainbow_color(self, size=3):
        """
        create a rainbow color generator
        :param size:
        :return:
        """
        isize = int(size/2)
        return self.sequence(
            self.linear_color(blue, green, size=isize),
            self.linear_color(green, red, size=isize)
        )

    def switch_color(self, colors =  [blue, green], times=10):
        """ 
        create switching colors, 
        """
        i = 0
        for j in range(0,times):
            color = colors[j % len(colors)]
            yield color


    #############################################################################
    # frame generators

    def clear(self, nbframes = 10):
        """
        ten frame display remove
        :return: a generator with black led_frames
        """
        empty = self.feed(self.all_leds, black)
        for i in range(0, nbframes):
            yield empty

    # generator for moving ring on the display
    def movering(self, direction, color):
        try:
            s = ""
            assert color is not None
            (f, t, s) = (0, 6, 1) if direction == 1 else (5, -1, -1)
            current = self.feed(self.all_leds, black)
            for i in range(f, t, s):
                s = self.ring(i, color)
                yield self.combine(current, s)
        except:
            traceback.print_exc()

    # generator for creating a color flash
    def flash(self, color, speed=5):

        buf = self.feed(self.all_leds, color)
        for i in range(0, speed):
            yield buf

        buf = self.feed(self.all_leds, black)
        for i in range(0, speed + 5):
            yield buf

    # generator for generating a wave
    def wave(self, color):
        # wave
        return self.sequence(self.movering(1, color),
                             self.movering(2, color))

    def rain(self, color):
        return self.sequence(self.dotAnim(color, length=1, space=27), self.clear())

    # generator for dots
    def dotAnim(self, color, length, space):
        for i in range(0, 2 * (length + space)):
            yield self.dots(color, length, i, space)

    def colored_square(self, color_generator, nbpatterns=2, squaresize=2, shift=0):
        for i in color_generator:
            yield self.square_pattern(i, nbpatterns=nbpatterns, square_size=squaresize, shift = shift)

    def randomDotColor(self):
        for i in range(0, self.all_leds):
            randomColor = (g, r, b) = (random.randint(0, 80), random.randint(0, 80), random.randint(0, 80))
            yield self.add(self.pixel(i, randomColor),
                           self.pixel(self.all_leds - i, randomColor))

    def dotAnimCg(self, colorgenerator, length, space):        
        l = map(lambda x:self.dotAnim(x,length,space), colorgenerator)
        anim = functools.reduce(lambda x,y:self.sequence(x,y), l)
        return anim


    ############################################################"
    # generator combiners

    # generator with a sequence of frames
    def sequence(self, frame_generator1, frame_generator2):
        if not frame_generator1 is None:
            for i in frame_generator1:
                yield i
        if not frame_generator2 is None:
            for j in frame_generator2:
                yield j

    # shift an animation
    def shift(self, frame_generator1, shift=10):
        return self.sequence(self.clear(shift), frame_generator1)

    def slow(self, frame_generator):
        for f in frame_generator:
            yield f
            yield f

    def fast(self, frame_generator):
        i = 0
        for f in frame_generator:
            if i == 0:
                yield f
            i = (i + 1) % 2

    # generator for parallel sequences
    def parallel(self, frame_generator1, frame_generator2, second_frame_shift=0):

        while not (frame_generator1 is None and frame_generator2 is None):
            s = None
            if frame_generator1 is not None:
                try:
                    s = next(frame_generator1)
                except StopIteration:
                    frame_generator1 = None
            s2 = None
            second_frame_shift = second_frame_shift - 1
            if frame_generator2 is not None and second_frame_shift <= 0:
                try:
                    s2 = next(frame_generator2)
                except StopIteration:
                    frame_generator2 = None
            yield self.add(s, s2)


def normaliseColor(c, level):
    (c1, c2, c3) = c
    v = (c1 + c2 + c3) / 3.0
    ratio = level * 1.0 / v
    return (min(int(ratio * c1), 255), (min(int(ratio * c2), 255)), (min(int(ratio * c3), 255)))
