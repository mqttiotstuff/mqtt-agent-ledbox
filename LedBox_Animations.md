
# Led Box Agent - MQTT Command parser

Making the led box "talk", an interpreter using several commands has been setted up to let users create their own patterns to be able to easily identify the event displayed.





# Examples (on run topic)

```
flash(red)

rain(green)

dotanim(blue, 1,10)

dotanim(red, 2, 5)

square(cgcolor(blue),3,3)

square(cglinear(blue,red,10),3,3)

slow(slow(dotanim(red, 1, 11)))

parallel(dotanim(red, 1, 11),rain(green))

parallel(parallel(dotanim(red, 1, 11),rain(blue)), dotanim(green,1,9))

sequence(square(cgcolor(blue),2,3), 

sequence(square(cgcolor(uired),2,1),sequence(square(cgcolor(blue),2,1), square(cgcolor(green),2,2))))

wave(blue)

sequence(wave(blue), shift(wave(green), 30))

parallel(shift(fg(fring(2,blue)),0),
        shift(fg(fring(1,green,)),10),
        shift(sequence(fg(fring(0,uipurple)), flash(uipurple)), 20))

sequence(parallel(slow(slow(square(cgcolor(uipurple),4,2))), rain(blue)), clear())

sequence(fg(fpixel(21,red),2),fg(fring(2,green)),fg(fpixel(22,red),2), clear()) 


sequence(
         parallel(
         slow(sequence(
                 fg(fpixel(21,red),2),
                 fg(fpixel(22,red),2),
                  fg(fpixel(23,red),2))),
         fg(fring(2,green)))
         , clear()) 
         
```



# Rational - API

There are 3 parts in the function references :

- some dealing with colors (constants, and variable)
- some dealing with color generators (permit to change colors in animations)
- some dealing with animations, and combining them
- some dealing with frames construction and enrich the vocabulary



Launching commands to MQTT, 

the python agent is listening to a specific "run" topic and take in the payload the expression to run, for example , running a rain feedback is launched using rain function and passing the color as argument

on topic `/home/agents/ledbox/run` and the following payload in raw utf-8 string :

```
rain(red)
```

will trigger this behaviour :



you can compose animations using the **parallel** or **sequence** function, as below, that let you combine in a parallel or one animation after an other way.

```
sequence( rain(red), rain(blue) )
```





## Function references

### Colors

the following colors are provided :

    "black"
    "green"
    "red
    "blue"
    "white"
    
    # colors from https://materialuicolors.co/
    "uipink"
    "uired"
    "uiblue"
    "uilightblue"
    "uipurple"
    "uideeppurple"
    "uiindigo"
    "uicyan"
    "uiteal"
    "uigreen"
    "uilightgreen"
    "uilime"
    "uiyellow"
    "uiamber"
    "uiorange"
    "uideeporange"
    "uibrown"
    "uigrey"
    "uibluegrey


### Animations

animations are `frame generators` there are the natural expression return of the interpreter. Some animation are already defined using the following function, but one can create some using the frame functions

#### clear()

fade the screen to black

#### rain(color)

create a rain animation, with the given color

#### random()

create an horizontal rain with random colors

#### flash(color, speed=5)

create a color flash, with the given speed

#### dotanim(color, length, space)

create a dot animation, moving remanent dots on the screen with the given length, and spaced by the space parmeter. Feedback can be very different depending on the parameters.

```
dotanim(red, 3, 20)
```

```
dotanim(red, 3, 7)
```

#### dotanim(color_generator, length, space)

same function as above, but take a color generator for changing the dot color during animation

example: 

```
dotanimcg(cglinear(green, blue), 3, 20)
```

#### movering(direction, color)

move a ring up or down, using the given color

direction=1 , mean down, 

direction = 0 , mean up

example :

```
movering(0, blue)
```

#### wave(color)

create a wave (down and up) using the given color, this function is equivalent to 

```
sequence(movering(1, blue), movering(0, blue))
```



#### square(color_generator, nbpatterns = 2, squaresize=2, shift=0)

create an animation with a square pattern sized squaresize in width, and the number of pattern repetition given with argument nbpatterns

the shift, is the offset in the pattern display



### Animation Modifiers

animation combiner permit to organize the play of animations.

#### sequence(frame_generator1, frame_generator2, frame_generator3, ...)

play the frame_generators in parameter one after the others



#### parallel(frame_generator1, frame_generator2, frame_generator3, ...)

play the frame_generators in parameter at the same time (in parallel). to adjust the timing the use of the `shift` function permit to delay an animation



#### slow(frame_generator)

this modifier take a frame generator and slow it down



#### fast(frame_generator)

this modifier speed up the animation in dropping intermediate frames.

example:

```
fast(rain(red))
```



### Colors Generators

Color generator create color ramps that are used in some animations. 



#### cglinear(fromcolor,tocolor,size=10)

create a linear color ramp from color "fromcolor" to  "tocolor", with "size" color in between.

#### cgcolor(color, framesize=5)

fixed color generator, keep the same color for the ramp.

#### cgrainbow(size=3)

create a rainbow color ramp from blue to green, then red with "size" colors

#### cgswitch(colors = [blue, green], times=10)

create the color ramps, following the given colors, 



### Frame functions

these following function create frames and permit to create new animations. Frames are created and then can be animated using the **fg()** function.



#### fring(h, color)

create a light ring frame at height "h" using color "color". 

#### fadd(frame1, frame2)

combine the two frames into one

#### fpixel(pixel_nb, color)

create a frame with only a pixel, at the "pixel_nb" position, using the color.

#### fdots(color, length=10, shift=0,space=10)

create a spaced dot line pattern frame

#### fg(frame, nbframe = 4) 

create a frame_generator from the given frame, using nbframe



