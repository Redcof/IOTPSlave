import os
import time
import datetime

home_dir = server_home = os.path.dirname(os.path.realpath(__file__))[:-9]

if os.path.exists("/home/pi"):
    LOG_PATH = '/home/pi/s4/iotp-slave-run.log'
else:
    LOG_PATH = home_dir + '/iotp-slave-run.log'


def log(string):
    global LOG_PATH
    fp = open(LOG_PATH, 'a')
    if fp is not None:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        string = st + ": " + string
        fp.write(string + "\n")
        fp.close()
    print string
    pass
