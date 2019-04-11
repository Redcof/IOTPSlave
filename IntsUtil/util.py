import os
import time
import datetime
import traceback
import sys

HOME_DIR = SERVER_HOME = os.path.dirname(os.path.realpath(__file__))[:-9]

if os.path.exists("/home/pi"):
    LOG_PATH = '/home/pi/s4/IOTPSlaveCore/iotp-slv-run.log'
    HOME_DIR = '/home/pi/s4/IOTPSlaveCore'
    SERVER_HOME = HOME_DIR
else:
    LOG_PATH = HOME_DIR + '/iotp-slv-run.log'

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def log(string, print_only=True):
    global LOG_PATH
    fp = open(LOG_PATH, 'a')
    if fp is not None and not print_only:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        string = st + ":[m]: " + str(string)
        fp.write(string + "\n")
        fp.close()
    print string
    pass


def log_error(e):
    global LOG_PATH
    tb = traceback.format_exc()
    fp = open(LOG_PATH, 'a')
    if fp is not None:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        string = st + ":[e]: " + e.message + " >> " + tb
        fp.write(string + "\n")
        fp.close()
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
