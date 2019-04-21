import os
import time
import datetime
import traceback
import sys

HOME_DIR = os.path.dirname(os.path.realpath(__file__))[:-9]
if os.path.exists("/home/pi"):
    LOG_PATH = '/home/pi/s4/activity.log'
else:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    LOG_PATH = current_dir + '/activity.log'

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def log(string):
    global LOG_PATH
    fp = open(LOG_PATH, 'a')
    if fp is not None:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        string = st + ":[m]: " + str(string)
        fp.write(string + "\n")
        fp.close()
    print string
    pass


def log_error(e):
    global LOG_PATH
    print e
    fp = open(LOG_PATH, 'a')
    if fp is not None:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        string = st + ":[e]: " + e.message
        fp.write(string + "\n")
        print_red(string)
        traceback.print_exc(file=fp)
        fp.close()
        pass
    pass


def print_red(e):
    sys.stdout.write(RED)
    print e
    sys.stdout.write(RESET)
    pass


def is_numeric(o):
    type_ = type(o).__name__
    # print type_
    if type_ == 'int' or type_ == 'float' or type_ == 'long':
        return True
    else:
        return False
    pass
