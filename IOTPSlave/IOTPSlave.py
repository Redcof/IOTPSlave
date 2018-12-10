import socket
import time
import re as regex

from IOTPTransactionResponse import IOTPTransactionResponse
from IOTPTransactionTypeInterrogation import IOTPTransactionTypeInterrogation
from IOTPTransactionData import IOTPTransactionData
from IOTPTransactionTypeCommand import IOTPTransactionTypeCommand
from S4Hw.S4HwInterface import init_gpio, operate_gpio_digital, operate_gpio_analog, get_gpio_status
from S4Timer.S4Timer import S4Timer

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

DIGITAL_OPERAND_TYPE = 0xd
ANALOG_OPERAND_TYPE = 0xa

DEFAULT_OPERAND = 0x0

PIN_NONE = -1

HARDWARE_CONF = [
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
]

INDEX_OPERAND_TYPE = 0
INDEX_OPERAND_ID = 1
INDEX_GPIO = 2
INDEX_OPERATION = 2


class IOTPSlave:

    def __init__(self, slave_home):
        self.init_ok = False
        self.slave_home = slave_home
        self.connection_ok = False
        self.handshake_done = False
        self.status_code = 0
        self.server_connection = None
        self.digital_operand_list = ""
        self.analog_operand_list = ""
        self.conn_retry_sec = 5
        self.server_offline_detection_timer = S4Timer(3, self.server_offline_detected)
        self.server_offline_detection = False
        pass

    @staticmethod
    def validate_conf_file():
        key_map = (KEY_HOST_IP, KEY_SLAVE_ID,
                   KEY_PORT, KEY_ANALOG_OPERAND_COUNT,
                   KEY_DIGITAL_OPERAND_COUNT)
        for k in key_map:
            if k not in IOTP_SLAVE_CONF:
                return False
        return True

    """ Load Configuration file """

    def init_slave(self):
        KEY = 0
        VALUE = 1
        doc = 0
        aoc = 0
        doc_calculated = 0
        aoc_calculated = 0

        dir_path = self.slave_home
        c_file = open(dir_path + '/iotp.slaveconf')

        # load the configuration to memory
        for line in c_file:
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

            for k in range(0, len(HARDWARE_CONF)):
                # check if digital operand
                try:
                    gpio = IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_PREFIX + str(k + 1)]
                    if gpio is not None:
                        HARDWARE_CONF[k] = (DIGITAL_OPERAND_TYPE, (k + 1), int(gpio))
                        doc_calculated += 1
                        self.digital_operand_list += "d{},".format(k + 1)
                        continue
                except:
                    pass

                # check if analog operand
                try:
                    gpio = IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_PREFIX + str(k + 1)]
                    if gpio is not None:
                        HARDWARE_CONF[k] = (ANALOG_OPERAND_TYPE, (k + 1), int(gpio))
                        aoc_calculated += 1
                        self.analog_operand_list += "a{},".format(k + 1)
                        continue
                except:
                    pass

            if doc is not doc_calculated or aoc is not aoc_calculated:
                self.status_code = 5  # number of operand and PIN configuration does not matched
                break

            self.digital_operand_list = self.digital_operand_list.rstrip(",")
            self.analog_operand_list = self.analog_operand_list.rstrip(",")

            # configure GPIO for HW operations
            init_gpio(HARDWARE_CONF, INDEX_GPIO)
            
            print HARDWARE_CONF

            self.init_ok = True
            print "Configuration OK"
            break  # while loop

        if self.init_ok is not True:
            print "Configuration filed"

    def init_connection(self):
        if self.init_ok is not True:
            return self.connection_ok

        """ Reset all parameters """
        ip = str(IOTP_SLAVE_CONF[KEY_HOST_IP])
        port = int(IOTP_SLAVE_CONF[KEY_PORT])

        self.server_offline_detection_timer.stop_timer()
        self.server_offline_detection = False

        print "Connecting to server..."

        while True:
            if self.connection_ok is True:
                break
            try:
                """ Connecting to server """
                self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_connection.setblocking(True)
                self.server_connection.connect((ip, port))
                self.connection_ok = True
                break
            except:
                self.server_connection = None
                print "Retry in " + str(self.conn_retry_sec) + " sec..."
                time.sleep(self.conn_retry_sec)
                print "Connecting..."

        print "Server Found."

        try:
            """ Send Connection Handshake """
            # byte://20/d:4[d1,d3,d4,d5]/a:2[a2,a6]
            init_req = "byte://{}/d:{}[{}]/a:{}[{}]\n".format(IOTP_SLAVE_CONF[KEY_SLAVE_ID],
                                                              IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_COUNT],
                                                              self.digital_operand_list,
                                                              IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_COUNT],
                                                              self.analog_operand_list)
            self.server_connection.sendall(init_req)
            print "TX: " + init_req
            """ Read response """
            response = self.read_line()
            print "RX: {}".format(response)

            res = regex.match(r"^\[(?P<status>[0-9]{3}),(?P<message>[A-z\s\d]+).*?\]$",
                              str(response), regex.I | regex.M)
            if res:
                res = res.groupdict()
            try:
                if int(res['status']) is 200:
                    self.handshake_done = True
                    print "Handshake OK."
                else:
                    print "Handshake Fail."
            except RuntimeError, e:
                print e

        finally:
            return self.connection_ok

    """ Communicate with IOTP Server """

    def communicate(self):
        if self.connection_ok is not True:
            return self.connection_ok

        print "Start Communication..."

        while self.connection_ok is True and self.handshake_done is True:
            # read data from server
            print 'Read command...'
            server_data = self.read_line()
            print "RX: {}".format(server_data)
            # if data available
            if server_data is not "" and server_data is not None:
                try:
                    iotp_response = IOTPTransactionResponse(400)
                    iotp_request = IOTPTransactionData(server_data, IOTP_SLAVE_CONF[KEY_SLAVE_ID])

                    # command request
                    if iotp_request.get_trans_type_id() is IOTPTransactionData.RequestType.COMMAND:
                        # process server data C 0001 0014 1 D 2 0001
                        r = IOTPTransactionTypeCommand(iotp_request)
                        while r.has_next():
                            inf = r.next_operand_info()
                            print 'operate: ', inf
                            operand_type = inf[INDEX_OPERAND_TYPE]
                            operand_id = inf[INDEX_OPERAND_ID]
                            operation = inf[INDEX_OPERATION]

                            try:
                                """ Search PIN """
                                HWConf = None
                                for k in range(0, len(HARDWARE_CONF)):
                                    hw_c = HARDWARE_CONF[k]
                                    if hw_c is not None and hw_c[INDEX_OPERAND_ID] is operand_id:
                                        HWConf = hw_c
                                        break

                                print HWConf
                                if HWConf is None:
                                    iotp_response.set_status(405)
                                    break
                                else:
                                    pin_type = HWConf[INDEX_OPERAND_TYPE]
                                    if pin_type == operand_type:
                                        pin = HWConf[INDEX_GPIO]
                                        if pin_type == DIGITAL_OPERAND_TYPE:
                                            # TODO Perform Digital Operation
                                            print operation, pin
                                            operate_gpio_digital(pin, operation)
                                            iotp_response.set_status(200)
                                            pass
                                        elif pin_type == ANALOG_OPERAND_TYPE:
                                            # TODO Perform Analog Operation
                                            operate_gpio_analog(pin, operation)
                                            iotp_response.set_status(200)
                                            pass
                            except RuntimeError, e:
                                print e
                                iotp_response.set_status(500)
                                iotp_response.set_message(e.message)
                                break
                    # interrogation request
                    elif iotp_request.get_trans_type_id() is IOTPTransactionData.RequestType.INTERROGATION:
                        # process server data D 0001 0014 D
                        # process server data D 0001 0014 C
                        intr = IOTPTransactionTypeInterrogation(iotp_request)
                        if intr.is_connection_check():
                            iotp_response.set_status(200)
                            pass
                        elif intr.is_status_check():
                            status = []
                            for k in range(0, len(HARDWARE_CONF)):
                                hw_c = HARDWARE_CONF[k]
                                if hw_c is not None:
                                    sts = get_gpio_status(hw_c[INDEX_GPIO])
                                    status.append({
                                        "id": hw_c[INDEX_OPERAND_ID],
                                        "type": hw_c[INDEX_OPERAND_TYPE],
                                        "state": sts
                                    })
                            iotp_response.set_status(200)
                            iotp_response.set_message(status)
                            pass
                        pass
                except:
                    pass
                print "TX: {}\\n".format(iotp_response.get_json())
                self.server_connection.sendall(iotp_response.get_json() + "\n")

        return self.connection_ok

    def read_line(self):
        if not isinstance(self.server_connection, socket.socket):
            raise Exception("Socket instance is required.")
        string = ""
        while self.connection_ok is True:
            try:
                """ Read one 1Byte """
                d = str(self.server_connection.recv(1))
                if len(d) is 0:
                    try:
                        """ Trying with a blank CR to check connection """
                        self.server_connection.sendall("\n")
                    except:
                        """ Server offline """
                        self.server_offline_detected()
                        break
                    if self.server_offline_detection is False:
                        self.server_offline_detection_timer.start_timer()
                        self.server_offline_detection = True
                    continue

                self.server_offline_detection_timer.stop_timer()
                self.server_offline_detection = False

                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except:
                pass

        return string

    def server_offline_detected(self):
        print "Server offline."
        self.server_connection = None
        self.connection_ok = False
        self.handshake_done = False
        pass
