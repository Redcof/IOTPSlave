import os
import time

from IOTPSlave.IOTPSlave import IOTPSlave
from IntsUtil import util
from IntsUtil.util import log

_author_ = "int_soumen"
_date_ = "16-Dec-2018"

# IOTP Slave Service.
# This service run on slave HW to operate relays and analog outputs

if __name__ == "__main__":
    _version_ = "2.1.7"
    log("Welcome to IOTP Slave version " + _version_, False)
    slave_home = util.HOME_DIR
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
    log("EXIT.", False)
