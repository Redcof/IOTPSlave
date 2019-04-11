from IntsUtil import util

_author_ = "int_soumen"
_date_ = "2018-11-17"
import json

# This file has been made to simulate virtual GPIO

VIRTUAL_GPIO = {}
JSON_FILE_PATH = util.HOME_DIR + "/operator-status.json"


# init GPIO pins
def init_gpio(gpio, mode='O', default=0):
    # prepare HW GPIO
    VIRTUAL_GPIO[gpio] = [mode, default]
    update_opr_sts_json()
    pass


# operate GPIO pins in DIGITAL
def operate_gpio_digital(gpio, operation):
    try:
        VIRTUAL_GPIO[gpio][1] = operation
    except KeyError:
        pass
    update_opr_sts_json()
    pass


# operate GPIO pins in PWM
def operate_gpio_analog(gpio, operation):
    VIRTUAL_GPIO[gpio][1] = operation
    update_opr_sts_json()
    pass


# get the any GPIO status
def get_gpio_status(gpio):
    return VIRTUAL_GPIO[gpio][1]


# update GPIO status to json file
def update_opr_sts_json():
    try:
        with open(JSON_FILE_PATH, "w") as data_file:
            json.dump(VIRTUAL_GPIO, data_file, indent=2)
            data_file.close()
            pass
        pass
    except Exception,e:
        pass
    pass
