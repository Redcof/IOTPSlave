_author_ = "int_soumen"
_date_ = "2018-11-17"

# This file has been made to simulate virtual GPIO

VIRTUAL_GPIO = {}


# init GPIO pins
def init_gpio(hw_conf, pin_index):
    # prepare HW GPIO
    for k in range(0, len(hw_conf)):
        pin = hw_conf[k]
        if pin is not None:
            VIRTUAL_GPIO[pin[pin_index]] = 0
    pass


# operate GPIO pins in DIGITAL
def operate_gpio_digital(gpio, operation):
    VIRTUAL_GPIO[gpio] = operation
    pass


# operate GPIO pins in PWM
def operate_gpio_analog(gpio, operation):
    VIRTUAL_GPIO[gpio] = operation
    pass


# get the any GPIO status
def get_gpio_status(gpio):
    return VIRTUAL_GPIO[gpio]
