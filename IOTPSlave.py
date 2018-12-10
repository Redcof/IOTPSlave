import socket
import time
import os

from IOTPTransactionData import IOTPTransactionData
from IOTPTransactionTypeCommand import IOTPTransactionTypeCommand

_author_ = "int_soumen"
_date_ = "02-08-2018"

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

DIGITAL_OPERAND = 0xd
ANALOG_OPERAND = 0xa

DEFAULT_OPERAND = 0x0

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


class IOTPSlave:

    def __init__(self):
        self.init_ok = False
        self.connection_ok = False
        self.status_code = 0
        self.conn = 0
        self.digital_operand_list = ""
        self.analog_operand_list = ""
        self.conn_retry_sec = 1
        pass

    def validate_conf_file(self):
        key_map = (KEY_HOST_IP, KEY_SLAVE_ID,
                   KEY_PORT, KEY_ANALOG_OPERAND_COUNT,
                   KEY_DIGITAL_OPERAND_COUNT)
        for k in key_map:
            if k not in IOTP_SLAVE_CONF:
                return False
        return True

    def init_slave(self):
        KEY = 0
        VALUE = 1
        doc = 0
        aoc = 0
        doc_calculated = 0
        aoc_calculated = 0

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
                IOTP_SLAVE_CONF[key] = value

        # validate configuration file
        while True:
            if self.validate_conf_file() is False:
                self.status_code = 1  # mandatory key not found
                break

            doc = int(IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_COUNT])
            aoc = int(IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_COUNT])

            if (doc + aoc) < 1:
                self.status_code = 2  # no operand found
                break

            if (doc + aoc) > 8:
                self.status_code = 3  # Maximum 8 operand can be configured
                break

            if aoc > 2:
                self.status_code = 4  # 2 analog operand can be configured
                break

            for k in HARDWARE_CONF:
                # check if digital operand
                try:
                    v = IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_PREFIX + str(k + 1)]
                    if v is not None:
                        HARDWARE_CONF[k] = (DIGITAL_OPERAND, int(v))
                        doc_calculated += 1
                        self.digital_operand_list += "d{},".format(k + 1)
                        continue
                except:
                    pass

                # check if analog operand
                try:
                    v = IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_PREFIX + str(k + 1)]
                    if v is not None:
                        HARDWARE_CONF[k] = (ANALOG_OPERAND, int(v))
                        aoc_calculated += 1
                        self.analog_operand_list += "a{},".format(k + 1)
                        continue
                except:
                    pass

            if doc is not doc_calculated or aoc is not aoc_calculated:
                self.status_code = 5  # number of operand and PIN configuration does not matched
                break

            self.init_ok = True
            print "Configuration OK"
            self.digital_operand_list = self.digital_operand_list.rstrip(",")
            self.analog_operand_list = self.analog_operand_list.rstrip(",")
            break  # while loop

        if self.init_ok is not True:
            print "Configuration filed"

    def init_connection(self):
        if self.init_ok is not True:
            return
        ip = str(IOTP_SLAVE_CONF[KEY_HOST_IP])
        port = int(IOTP_SLAVE_CONF[KEY_PORT])

        print "Connecting to server..."
        while True:
            if self.connection_ok is True:
                break
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            try:
                while True:
                    # byte://20/d:4[d1,d3,d4,d5]/a:2[a2,a6]
                    init_req = "byte://{}/d:{}[{}]/a:{}[{}]\n".format(IOTP_SLAVE_CONF[KEY_SLAVE_ID],
                                                                      IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_COUNT],
                                                                      self.digital_operand_list,
                                                                      IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_COUNT],
                                                                      self.analog_operand_list)
                    sock.sendall(init_req)
                    print "TX: " + init_req
                    response = self.read_line(sock, True)
                    print "RX: {}".format(response)
                    try:
                        if int(response) is 200:
                            self.connection_ok = True
                            self.conn = sock
                            print "Connection OK"
                            break
                    except:
                        break
                    print "Failed."
                    print "Retry in {} second(s)...".format(self.conn_retry_sec)
                    time.sleep(self.conn_retry_sec)
            finally:
                pass

    # this function is a complete client implementation
    def communicate(self):
        if self.connection_ok is not True:
            return

        print "Communicating..."

        while True:
            server_data = self.read_line(self.conn)
            print "RX: {}".format(server_data)
            time.sleep(.2)
            if server_data is not "":
                # process server data C000200151D10001
                x = IOTPTransactionData(server_data, IOTP_SLAVE_CONF[KEY_SLAVE_ID])
                if x.get_trans_type_id() is IOTPTransactionData.RequestType.COMMAND:
                    r = IOTPTransactionTypeCommand(x)
                    while r.has_next():
                        inf = r.next_operand_info()
                        print inf

                print "TX: 200\\n"
                self.conn.sendall("200\n")

    def read_line(self, conn, blocking=False):
        if not isinstance(conn, socket.socket):
            raise Exception("Socket instance is required.")
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
