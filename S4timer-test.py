from S4Timer import S4Timer

flag = True


def g():
    global flag
    print "Timer 1"
    # flag = False
    timer.release_timer()


def g2(obj):
    global flag
    print obj
    flag = False
    timer2.release_timer()


timer = S4Timer(5, g)
timer.start_timer()

timer2 = S4Timer(10, g2, {"Hello"})
# timer2.start_timer()

while flag:
    pass
