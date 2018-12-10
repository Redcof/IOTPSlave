from IOTPSlave import IOTPSlave

_author_ = "int_soumen"
_date_ = "02-08-2018"


# IOTP Slave Service.
# This service run on slave HW to operate relays and analog outputs


slave = IOTPSlave()
slave.init_slave()
slave.connect()