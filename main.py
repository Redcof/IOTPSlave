import os
import time

from IOTPSlaveCore.IOTPSlave import IOTPSlave
from IntsUtil import util
from IntsUtil.util import log

_author_ = "int_soumen"
_date_ = "16-Dec-2018"

# IOTP Slave Service.
# This service run on slave HW to operate relays and analog outputs

if __name__ == "__main__":
    _version_ = "3.5.0"
    log("Welcome to IOTP Slave version " + _version_)
    slave_home = os.path.dirname(os.path.realpath(__file__))
    slave = IOTPSlave(slave_home)
    slave.init_slave()

    try:
        while True:
            if slave.init_connection() is True:
                if slave.start_server() is True:
                    break
            time.sleep(5)
        while True:
            time.sleep(5000)
    except KeyboardInterrupt, e:
        slave.stop()
        pass
    log("EXIT.")
