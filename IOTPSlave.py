import socket
import time
import os

_author_ = "int_soumen"
_date_ = "02-08-2018"


class IOTPSlave:
    IOTP_SLAVECONF = {}
    KEY_DIGITAL_OPERAND_COUNT = "digital"
    KEY_ANALOG_OPERAND_COUNT = "analog"
    KEY_DIGITAL_OPERAND_PREFIX = "d"
    KEY_ANALOG_OPERAND_PREFIX = "a"
    KEY_SLAVE_ID = "id"
    KEY_HOST_IP = "host"
    KEY_PORT = "port"
    KEY_AUTHOR = "author"
    KEY_DATE = "date"

    DIGITAL_OPERAND = 0
    ANALOG_OPERAND = 1

    DEFAULT_OPERAND = -1

    PIN_NONE = -1

    HARDWARE_CONF = {
        0x0: None,
        0x1: None,
        0x2: None,
        0x3: None,
        0x4: None,
        0x5: None,
        0x6: None,
        0x7: None,
    }

    INDEX_OPERAND_TYPE = 0
    INDEX_OPERAND_PIN = 1

    def __init__(self):
        pass

    def init_slave(self):
        KEY = 0
        VALUE = 1

        dir_path = os.path.dirname(os.path.realpath(__file__))
        f = open(dir_path + '/iotp.slaveconf')
        # load the configuration to memory
        for line in f:
            # skip comments
            if line[0] is "#":
                continue
            components = line.split("=", 1)
            if len(components) > 1:
                # Skip comments inside values
                key = components[KEY].strip(" ").rstrip("\n")
                value = components[VALUE].split("#", 1)[0].strip(" ").rstrip("\n")
                self.IOTP_SLAVECONF[key] = value

        # configure the hardware conf
        for k in self.HARDWARE_CONF:
            # check if digital operand
            try:
                v = self.IOTP_SLAVECONF[self.KEY_DIGITAL_OPERAND_PREFIX + str(k + 1)]
                if v is not None:
                    self.HARDWARE_CONF[k] = (self.DIGITAL_OPERAND, int(v))
                    continue
            except:
                pass

            # check if analog operand
            try:
                v = self.IOTP_SLAVECONF[self.KEY_ANALOG_OPERAND_PREFIX + str(k + 1)]
                if v is not None:
                    self.HARDWARE_CONF[k] = (self.ANALOG_OPERAND, int(v))
                    continue
            except:
                pass

        print self.HARDWARE_CONF

    # this function is a complete client implementation
    def connect(self):
        # hostname = socket.gethostname()
        # IPAddr = socket.gethostbyname(hostname)
        ip = str(self.IOTP_SLAVECONF[self.KEY_HOST_IP])
        port = int(self.IOTP_SLAVECONF[self.KEY_PORT])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            # sock.sendall(message + "\n")
            #  initiate connection
            while True:
                # byte://20/d/2/a/2
                msg = "byte://{}/d/{}/a/{}\n".format(self.IOTP_SLAVECONF[self.KEY_SLAVE_ID],
                                                     self.IOTP_SLAVECONF[self.KEY_DIGITAL_OPERAND_COUNT],
                                                     self.IOTP_SLAVECONF[self.KEY_ANALOG_OPERAND_COUNT])
                sock.sendall(msg)
                print "TX: " + msg
                response = self.read_line(sock)
                print "RX: {}".format(response)
                time.sleep(1)
        finally:
            sock.close()

    def read_line(self, conn):
        string = ""
        while True:
            try:
                d = str(conn.recv(1))
                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except:
                break
        return string
