
# Led Box animation experiments

function references

Using colors


Using patterns


Using animation time


examples (on run topic)

flash(red)
rain(green)
dotanim(blue, 1,10)
dotanim(red, 2, 5)
square(cgcolor(blue),3,3)
square(cglinear(blue,red,10),3,3)

slow(slow(dotanim(red, 1, 11)))

parallel(dotanim(red, 1, 11),rain(green))

parallel(parallel(dotanim(red, 1, 11),rain(blue)), dotanim(green,1,9))

sequence(square(cgcolor(blue),2,3), sequence(square(cgcolor(uired),2,1),sequence(square(cgcolor(blue),2,1), square(cgcolor(green),2,2))))

wave(blue)

sequence(wave(blue), shift(wave(green), 30))

parallel(shift(fg(fring(2,blue)),0),
        shift(fg(fring(1,green,)),10),
        shift(sequence(fg(fring(0,uipurple)), flash(uipurple)), 20))

