import RPi.GPIO as GPIO

_author_ = "int_soumen"
_date_ = "2019-09-26"

# Reference http://wiringpi.com/the-gpio-utility/
# Reference https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/

_INIT_DONE = False


# init GPIO pins
def init_gpio(gpio, mode='O', default=0):
    global _INIT_DONE
    # prepare HW GPIO
    if _INIT_DONE is False:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)
        _INIT_DONE = True
    if mode is 'O':
        GPIO.setup(gpio, GPIO.OUT)
        if default is 0:
            GPIO.output(gpio, GPIO.HIGH)
        if default is 1:
            GPIO.output(gpio, GPIO.LOW)
    if mode is 'I':
        GPIO.setup(gpio, GPIO.IN)


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
