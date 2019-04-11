import os
import socket
import threading
import time
import re as regex
from thread import start_new_thread

from IOTPTransactionResponse import IOTPTransactionResponse
from IOTPTransactionTypeInterrogation import IOTPTransactionTypeInterrogation
from IOTPTransactionData import IOTPTransactionData
from IOTPTransactionTypeCommand import IOTPTransactionTypeCommand
from IntsUtil import util
from IntsUtil.util import log, log_error
from IntsSQLiteAccess import DatabaseManager
from S4Hw.S4Blink import S4LED

if os.path.exists("/home/pi"):
    from S4Hw.S4HwInterface import init_gpio, operate_gpio_digital, operate_gpio_analog, get_gpio_status

    SLEEP_WAIT = 20
else:
    from S4Hw.dev_S4HwInterface import init_gpio, operate_gpio_digital, operate_gpio_analog, get_gpio_status

    SLEEP_WAIT = 0

_author_ = "int_soumen"
_date_ = "02-08-2018"
_date_mod_ = "31-Mar-2019"

IOTP_SLAVE_CONF = {}
KEY_STATUS_LED = "led"
KEY_DIGITAL_OPERAND_COUNT = "don"
KEY_ANALOG_OPERAND_COUNT = "aon"
KEY_DIGITAL_OPERAND_PREFIX = "d"
KEY_ANALOG_OPERAND_PREFIX = "a"
KEY_SLAVE_ID = "usid"
KEY_HOST_IP = "host"
KEY_HOST_PORT = "host_port"
KEY_PORT = "port"
KEY_AUTHOR = "author"
KEY_DATE = "date"

DIGITAL_OPERAND_TYPE = 0xd
ANALOG_OPERAND_TYPE = 0xa

DEFAULT_OPERAND = 0x0

PIN_NONE = -1

# maximum 8 HW
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

STATUS_LED_GPIO = 3
blink_level = 0


class IOTPSlave:

    def __init__(self, slave_home):
        global SLEEP_WAIT
        time.sleep(SLEEP_WAIT)
        # init_gpio(STATUS_LED_GPIO, 'O', 0)
        self.StatusLED = S4LED(STATUS_LED_GPIO)
        self.init_ok = False
        self.slave_home = slave_home
        self.connection_status = False
        self.handshake_done = False
        self.status_code = 0
        # self.server_sock = None
        self.slave_server = None
        self.digital_operand_list = ""
        self.analog_operand_list = ""
        self.conn_retry_sec = 5
        # self.server_offline_detection_timer = S4Timer(3, self.server_offline_detected)
        # self.server_offline_detection = False
        self.sts_blink = False
        self.blink_pause = 0.2
        self.blink_retain = 0.1
        self.start_blinking()
        self.DB = DatabaseManager.Database(util.SERVER_HOME + "/s4.db")
        # self.iron_rod = HotFlag(20)
        pass

    @staticmethod
    def fn_validate_conf_file():
        key_map = (KEY_HOST_IP, KEY_SLAVE_ID, KEY_STATUS_LED,
                   KEY_HOST_PORT, KEY_PORT, KEY_ANALOG_OPERAND_COUNT,
                   KEY_DIGITAL_OPERAND_COUNT)
        for k in key_map:
            if k not in IOTP_SLAVE_CONF:
                return False
        return True

    """ Load Configuration file """

    def init_slave(self):
        KEY = 0
        VALUE = 1
        digital_operand_count = 0
        analog_operand_count = 0
        doc_calculated = 0
        aoc_calculated = 0
        log("IN CONFIG...", False)
        conf_file_path = self.slave_home + '/iotp.slaveconf'
        c_file = open(conf_file_path)

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
            if self.fn_validate_conf_file() is False:
                self.status_code = 1  # mandatory key not found
                break

            # init status LED GPIO
            # STATUS_LED_GPIO = int(IOTP_SLAVE_CONF[KEY_STATUS_LED])
            # operate_gpio_digital(STATUS_LED_GPIO, 1)

            digital_operand_count = int(IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_COUNT])
            analog_operand_count = int(IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_COUNT])

            if (digital_operand_count + analog_operand_count) < 1:
                self.status_code = 2  # no operand found
                break

            if (digital_operand_count + analog_operand_count) > 8:
                self.status_code = 3  # Maximum 8 operand can be configured
                break

            if analog_operand_count > 2:
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
                except Exception, e:
                    # log_error(e)
                    pass

                # check if analog operand
                try:
                    gpio = IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_PREFIX + str(k + 1)]
                    if gpio is not None:
                        HARDWARE_CONF[k] = (ANALOG_OPERAND_TYPE, (k + 1), int(gpio))
                        aoc_calculated += 1
                        self.analog_operand_list += "a{},".format(k + 1)
                        continue
                except Exception, e:
                    # log_error(e)
                    pass

            if digital_operand_count is not doc_calculated or analog_operand_count is not aoc_calculated:
                self.status_code = 5  # number of operand and PIN configuration does not matched
                break

            self.digital_operand_list = self.digital_operand_list.rstrip(",")
            self.analog_operand_list = self.analog_operand_list.rstrip(",")

            # configure GPIO for HW operations
            for k in range(0, len(HARDWARE_CONF)):
                pin = HARDWARE_CONF[k]
                if pin is not None:
                    init_gpio(pin[INDEX_GPIO], 'O', 0)

            # print HARDWARE_CONF
            # print IOTP_SLAVE_CONF

            self.init_ok = True
            log("CONFIG OK.", False)
            self.start_blinking()
            break  # while loop

        if self.init_ok is not True:
            log("CONFIG FAILED.", False)
            self.blink_pause = 1
            self.start_blinking()

    def start_blinking(self):
        global blink_level
        if self.sts_blink is False:
            blink_level = (blink_level + 1)
            self.sts_blink = True
            start_new_thread(self.blink, (1,))
        pass

    def stop_blinking(self, closing_value=0):
        global blink_level
        blink_level = (blink_level - 1)
        self.sts_blink = False
        time.sleep(1)
        start_new_thread(self.blink, (closing_value,))
        pass

    def blink(self, closing_value):
        global blink_level
        print "blinking... LEVEL" + str(blink_level)
        while self.sts_blink is True:
            self.StatusLED.off()
            time.sleep(self.blink_pause)
            self.StatusLED.on()
            time.sleep(self.blink_retain)
        operate_gpio_digital(STATUS_LED_GPIO, closing_value)
        print "blink end. LEVEL" + str(blink_level)

    def init_connection(self):
        if self.init_ok is not True:
            return False

        server_ip = str(IOTP_SLAVE_CONF[KEY_HOST_IP])
        port = int(IOTP_SLAVE_CONF[KEY_HOST_PORT])

        # self.server_offline_detection_timer.stop_timer()
        # self.server_offline_detection = False

        log("FINDING SERVER @{}...".format((server_ip, port)))
        while True:
            # if self.connection_status is True:
            #     break
            try:
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setblocking(True)
                server_sock.connect((server_ip, port))
                self.connection_status = True
                break
            except Exception, e:
                print e
                self.start_blinking()
                self.connection_status = False
                log("RETRY...")
                time.sleep(self.conn_retry_sec - 1)
        log("CONNECTED.OK.")
        # stop blinking
        self.stop_blinking()

        try:
            """ Send Connection Handshake """
            # byte://20/d:4[d1,d3,d4,d5]/a:2[a2,a6]
            init_req = "byte://{}/d:{}[{}]/a:{}[{}]\n".format(IOTP_SLAVE_CONF[KEY_SLAVE_ID],
                                                              IOTP_SLAVE_CONF[KEY_DIGITAL_OPERAND_COUNT],
                                                              self.digital_operand_list,
                                                              IOTP_SLAVE_CONF[KEY_ANALOG_OPERAND_COUNT],
                                                              self.analog_operand_list)
            server_sock.sendall(init_req)
            log("TX: >> " + init_req)
            """ Read response """
            response = self._fn_read_line(server_sock)
            log("RX: << {}".format(response))

            res = regex.match(r"^\[(?P<status>[0-9]{3}),(?P<message>[A-z\s\d]+).*?\]$",
                              str(response), regex.I | regex.M)
            if res:
                res = res.groupdict()
            try:
                if int(res['status']) is 200:
                    self.handshake_done = True
                    log("HANDSHAKE.OK.")
                else:
                    self.handshake_done = False
                    log("HANDSHAKE.FAIL.")
            except RuntimeError, e:
                self.connection_status = False
                log_error(e)
        finally:
            threading.Timer(20.0, self.init_connection).start()
            return self.connection_status
        pass

    """ NEW STATELESS SLAVE """

    def start_server(self):
        if self.connection_status is not True or self.handshake_done is not True:
            return False

        if self.slave_server is None:
            self.start_blinking()

            # bind socket with IP and PORT
            try:
                port = int(IOTP_SLAVE_CONF[KEY_PORT])
                log("CREATING SLAVE SERVER @ PORT{}...".format(port), False)
                while True:
                    try:
                        self.slave_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.slave_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.slave_server.bind(('', port))
                        break
                    except Exception, e:
                        log_error(e)
                        time.sleep(1)

                        # start listing to the incoming connection
                log('SLAVE SERVER OK.RUNNING.', False)
                self.stop_blinking()
                self.s_listen()
                return True
            except Exception, e:
                log_error(e)
                return False
        else:
            return False
        pass

    def s_listen(self):
        BACK_LOG = 1
        # listen for new incoming connection
        self.slave_server.listen(BACK_LOG)

        while True:
            log("WAIT FOR CMD...")
            # accept a new connection
            conn, addr = self.slave_server.accept()
            log("RECEIVED")
            # start a thread with client request

            self.sts_blink = True
            start_new_thread(self.blink, (0,))
            self.sts_blink = False

            start_new_thread(self.command_process, (conn, addr,))

    def stop(self):
        if self.slave_server is not None:
            self.slave_server.close()
            # self.server_sock = None
            self.connection_status = False
            self.handshake_done = False
            operate_gpio_digital(STATUS_LED_GPIO, 1)

    """ Communicate with IOTP Server """

    def _communicate(self, in_server_conn, server_data):
        # read data from server
        log("RX: {}".format(server_data))
        # if data available
        if server_data is not "" and server_data is not None:
            try:
                iotp_response = IOTPTransactionResponse(400, IOTP_SLAVE_CONF[KEY_SLAVE_ID])
                iotp_request = IOTPTransactionData(server_data, IOTP_SLAVE_CONF[KEY_SLAVE_ID])

                # command request
                if iotp_request.get_trans_type_id() is IOTPTransactionData.RequestType.COMMAND:
                    # process server data C 0001 0014 1 D 2 0001
                    r = IOTPTransactionTypeCommand(iotp_request)
                    while r.has_next():
                        inf = r.next_operand_info()

                        operand_type = inf[INDEX_OPERAND_TYPE]
                        operand_id = inf[INDEX_OPERAND_ID]
                        operation = inf[INDEX_OPERATION]

                        try:
                            """ Search PIN """
                            HWConf = None
                            for k in range(0, len(HARDWARE_CONF)):
                                hw_c = HARDWARE_CONF[k]
                                if hw_c is not None and hw_c[INDEX_OPERAND_ID] is operand_id:
                                    """ PIN Found """
                                    HWConf = hw_c
                                    self.save_to_database(operand_id, operation)
                                    break
                            if HWConf is None:
                                iotp_response.set_status(405)
                                break
                            else:
                                pin_type = HWConf[INDEX_OPERAND_TYPE]
                                if pin_type == operand_type:
                                    pin = HWConf[INDEX_GPIO]
                                    if pin_type == DIGITAL_OPERAND_TYPE:
                                        # Change the operation value as the relays are active low
                                        if operation is 0:
                                            operation = 1
                                        else:
                                            operation = 0

                                        # Perform Digital Operation
                                        operate_gpio_digital(pin, operation)
                                        iotp_response.set_status(200)
                                        pass
                                    elif pin_type == ANALOG_OPERAND_TYPE:
                                        # Perform Analog Operation
                                        operate_gpio_analog(pin, operation)
                                        iotp_response.set_status(200)
                                        pass
                        except RuntimeError, e:
                            print e
                            log_error(e)
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
                                if sts is 0:
                                    sts = 1
                                else:
                                    sts = 0
                                status.append({
                                    "id": hw_c[INDEX_OPERAND_ID],
                                    "type": hw_c[INDEX_OPERAND_TYPE],
                                    "state": sts
                                })
                        iotp_response.set_status(200)
                        iotp_response.set_message(status)
                        pass
                    pass
                log("TX: {}\\n".format(iotp_response.get_json()))
                in_server_conn.sendall(iotp_response.get_json() + "\n")
            except Exception, e:
                print e
                log_error(e)
                pass

    # handle client in a thread
    def command_process(self, in_server_conn, addr):
        # read client request line
        cmd_data = self._fn_read_line(in_server_conn)
        if cmd_data is None:
            in_server_conn.close()
            return
        self._communicate(in_server_conn, cmd_data)
        return
        pass

    def save_to_database(self, operand_id, operation):
        """ DATABASE OPERATION """
        log("Save to Database")
        self.DB.connect()
        self.DB.query(
            "INSERT INTO s4_operation_log(operation_time, slave_id, opration_type) VALUES (?, ?, ?)",
            (time.time(), operand_id, operation)
        )
        self.DB.commit()
        self.DB.disconnect()
        pass

    @staticmethod
    def _fn_read_line(conn):
        string = ""
        while True:
            try:
                d = str(conn.recv(1))
                if len(d) is 0:
                    try:
                        """ Trying with a CR to check connection """
                        conn.sendall("\n")
                    except Exception, e:
                        """ Server offline """
                        string = None
                        break
                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except Exception, e:
                string = None
                break
        return string
        pass
