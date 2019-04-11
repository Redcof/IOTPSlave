import os
import time
from thread import start_new_thread

from IntsUtil.util import is_numeric

if os.path.exists("/home/pi"):
    from S4Hw.S4HwInterface import init_gpio, operate_gpio_digital
else:
    from S4Hw.dev_S4HwInterface import init_gpio, operate_gpio_digital

_author_ = "int_soumen"
_date_ = "2019-04-02"


class S4LED:
    def __init__(self, gpio):
        self.gpio = gpio
        init_gpio(gpio, 'O', 0)
        self.blinking_status = False
        self.blinking_delay_sec = 0.5
        self.led_retention_sec = 0.5
        # self.operation_status = False
        self.closing_value = 0
        # self.thread_status = False
        # self.blink_level_ctr = 0
        # self.recover()
        pass

    def operate(self):
        for i in range(0, 3, 1):
            operate_gpio_digital(self.gpio, 1)
            time.sleep(self.led_retention_sec)
            operate_gpio_digital(self.gpio, 0)
            time.sleep(self.blinking_delay_sec)
            pass
        operate_gpio_digital(self.gpio, self.closing_value)

    # def get_conf(self):
    #     return self.blinking_delay_sec, self.led_retention_sec
    #     pass
    #
    # def set_conf(self, conf):
    #     self.blinking_delay_sec = conf[0]
    #     self.led_retention_sec = conf[1]
    #     pass

    def blink(self, mode="normal", retention="normal", closing_value=0):
        # self.blink_level_ctr = self.blink_level_ctr + 1

        if is_numeric(mode):
            self.blinking_delay_sec = mode
        elif mode == "normal":
            self.blinking_delay_sec = 0.5  # 500 msec
        elif mode == "fast":
            self.blinking_delay_sec = 0.2  # 200 msec
        elif mode == "slow":
            self.blinking_delay_sec = 1  # 1000 msec
        elif mode == "lazy":
            self.blinking_delay_sec = 3  # 3000 msec
        else:
            self.blinking_delay_sec = 0.5  # 500 msec

        if is_numeric(retention):
            self.blinking_delay_sec = retention
        elif retention == "normal":
            self.led_retention_sec = 0.5  # 500 msec
        elif retention == "long":
            self.led_retention_sec = 3  # 3000 msec
        elif retention == "short":
            self.led_retention_sec = 0.2  # 200 msec
        elif retention == "tiny":
            self.led_retention_sec = 0.05  # 50 msec
        else:
            self.led_retention_sec = 0.5  # 500 msec

        # self.operation_status = True
        self.closing_value = closing_value

        start_new_thread(self.operate, ())
        pass

    # def stop_blink(self, closing_value=0):
    #     # self.blink_level_ctr = self.blink_level_ctr - 1
    #     self.closing_value = closing_value
    #     if self.blink_level_ctr == 0:
    #         self.operation_status = False
    #     else:
    #         operate_gpio_digital(self.gpio, self.closing_value)
    #     pass
    #
    # def kill(self):
    #     # self.thread_status = False
    #     pass
    #
    # def recover(self):
    #     # if self.thread_status is False:
    #     #     self.thread_status = True
    #     #     start_new_thread(self.operate, ())
    #     pass

    def on(self):
        operate_gpio_digital(self.gpio, 1)
        pass

    def off(self):
        operate_gpio_digital(self.gpio, 0)
        pass
