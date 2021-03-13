

def fn(parameter):
    for i in range(0,10):
        yield parameter

def sequence(f1,f2):
    for i in f1:
        yield i


def combine(f1,f2):

    endF1 = not f1 is None
    endF2 = not f2 is None

    while True:
        if not endF1:
            try:
                yield next(f1)
            except StopIteration:
                endF1 = True
        if not endF2:
            try:
                yield next(f2)
            except StopIteration:
                endF2 = True
        if endF1 and endF2:
            break

while (fn(0).__next__()):
    print("hello")
    pass
print("done")

for j in combine(fn(0),fn(1)):
    print(j)


