import socket
import time
import os

_author_ = "int_soumen"
_date_ = "02-08-2018"


class IOTPSlave:
    IOTP_SLAVE_CONF = {}
    KEY_DIGITAL_OPERAND_COUNT = "don"
    KEY_ANALOG_OPERAND_COUNT = "aon"
    KEY_DIGITAL_OPERAND_PREFIX = "d"
    KEY_ANALOG_OPERAND_PREFIX = "a"
    KEY_SLAVE_ID = "usid"
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
        self.init_ok = False
        self.connection_ok = False
        self.status_code = 0
        self.conn = 0
        pass

    def validate_conf_file(self):
        key_map = (self.KEY_HOST_IP, self.KEY_SLAVE_ID,
                   self.KEY_PORT, self.KEY_ANALOG_OPERAND_COUNT,
                   self.KEY_DIGITAL_OPERAND_COUNT)
        for k in key_map:
            if k not in self.IOTP_SLAVE_CONF:
                return False
        return True

    def init_slave(self):
        KEY = 0
        VALUE = 1
        don = 0
        aon = 0
        don_calculated = 0
        aon_calculated = 0

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file = open(dir_path + '/iotp.slaveconf')

        # load the configuration to memory
        for line in file:
            # skip comments
            if line[0] is "#":
                continue
            components = line.split("=", 1)
            if len(components) > 1:
                # Skip comments inside values
                key = components[KEY].strip(" ").rstrip("\n")
                value = components[VALUE].split("#", 1)[0].strip(" ").rstrip("\n")
                self.IOTP_SLAVE_CONF[key] = value

        # validate configuration file
        while True:
            if self.validate_conf_file() is False:
                self.status_code = 1  # mandatory key not found
                break

            don = int(self.IOTP_SLAVE_CONF[self.KEY_DIGITAL_OPERAND_COUNT])
            aon = int(self.IOTP_SLAVE_CONF[self.KEY_ANALOG_OPERAND_COUNT])

            if (don + aon) < 1:
                self.status_code = 2  # no operand found
                break

            if (don + aon) > 8:
                self.status_code = 3  # Maximum 8 operand can be configured
                break

            if aon > 2:
                self.status_code = 4  # 2 analog operand can be configured
                break

            for k in self.HARDWARE_CONF:
                # check if digital operand
                try:
                    v = self.IOTP_SLAVE_CONF[self.KEY_DIGITAL_OPERAND_PREFIX + str(k + 1)]
                    if v is not None:
                        self.HARDWARE_CONF[k] = (self.DIGITAL_OPERAND, int(v))
                        don_calculated += 1
                        continue
                except:
                    pass

                # check if analog operand
                try:
                    v = self.IOTP_SLAVE_CONF[self.KEY_ANALOG_OPERAND_PREFIX + str(k + 1)]
                    if v is not None:
                        self.HARDWARE_CONF[k] = (self.ANALOG_OPERAND, int(v))
                        aon_calculated += 1
                        continue
                except:
                    pass

            if don is not don_calculated or aon is not aon_calculated:
                self.status_code = 5  # number of operand and PIN configuration does not matched
                break

            self.init_ok = True
            print "Configuration OK"
            break  # while loop

        if self.init_ok is not True:
            print "Configuration filed"

    def init_connection(self):
        if self.init_ok is not True:
            return
        ip = str(self.IOTP_SLAVE_CONF[self.KEY_HOST_IP])
        port = int(self.IOTP_SLAVE_CONF[self.KEY_PORT])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Connecting to server..."
        sock.connect((ip, port))

        try:
            while True:
                # byte://20/d/2/a/2
                init_req = "byte://{}/d/{}/a/{}\n".format(self.IOTP_SLAVE_CONF[self.KEY_SLAVE_ID],
                                                          self.IOTP_SLAVE_CONF[self.KEY_DIGITAL_OPERAND_COUNT],
                                                          self.IOTP_SLAVE_CONF[self.KEY_ANALOG_OPERAND_COUNT])
                sock.sendall(init_req)
                print "TX: " + init_req
                response = self.read_line(sock, True)
                print "RX: {}".format(response)
                if int(response) is not 200:
                    self.connection_ok = True
                    self.conn = sock
                    print "Connection OK"
                    break
                time.sleep(1)
        finally:
            pass

    # this function is a complete client implementation
    def communicate(self):
        if self.connection_ok is not True:
            return

        print "Communicating..."

        while True:
            response = self.read_line(self.conn)
            print "RX: {}".format(response)
            time.sleep(.2)
            self.conn.sendall("")

    def read_line(self, conn, blocking=False):
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
