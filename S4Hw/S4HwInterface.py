import RPi.GPIO as GPIO
import subprocess

_author_ = "int_soumen"
_date_ = "2019-09-26"


# Reference http://wiringpi.com/the-gpio-utility/
# Reference https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/

# init GPIO pins
def init_gpio(hw_conf, pin_index):
    # prepare HW GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for k in range(0, len(hw_conf)):
        pin = hw_conf[k]
        if pin is not None:
            GPIO.setup(pin[pin_index], GPIO.OUT)
            GPIO.output(pin[pin_index], GPIO.HIGH)


# operate GPIO pins in DIGITAL
def operate_gpio_digital(gpio, operation):
    if operation is 1:
        GPIO.output(gpio, GPIO.HIGH)
    if operation is 0:
        GPIO.output(gpio, GPIO.LOW)


# operate GPIO pins in PWM
def operate_gpio_analog(gpio, operation):
    pass


# get the any GPIO status
def get_gpio_status(gpio):
    v = GPIO.input(gpio)
    return v
