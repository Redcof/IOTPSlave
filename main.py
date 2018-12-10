from IOTPSlave import IOTPSlave
import time

_author_ = "int_soumen"
_date_ = "02-08-2018"

# IOTP Slave Service.
# This service run on slave HW to operate relays and analog outputs

if __name__ == "__main__":
    _version_ = "1.0.0"
    print "Welcome to IOTP Slave version " + _version_

    slave = IOTPSlave()
    slave.init_slave()

    while True:
        if slave.init_connection() is True:
            if slave.communicate() is False:
                time.sleep(5)
                continue
        break
    print "Unable establish connection."
