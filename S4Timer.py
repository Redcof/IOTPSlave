from thread import *
import time

_author_ = "int_soumen"
_date_ = "16-09-2018"


class S4Timer:
    STATE_IDLE = 1
    STATE_ACTIVE = 2
    STATE_EXPIRED = 3
    STATE_RELEASE_REQUEST = 4

    def __init__(self, timeout_sec, callback, data = None):
        self.Timeout = timeout_sec
        self.en_ThState = S4Timer.STATE_IDLE
        self.TimeStartTime = -1
        self.Data = data
        if callback is not None:
            self.Callback = callback
            pass
        start_new_thread(self.run, ())


    """ reset timer """

    def reset_timer(self):
        self.en_ThState = S4Timer.STATE_ACTIVE
        self.TimeStartTime = time.time()

    """ start timer """

    def start_timer(self):
        self.en_ThState = S4Timer.STATE_ACTIVE
        self.TimeStartTime = time.time()

    """ stop timer """

    def stop_timer(self):
        self.en_ThState = S4Timer.STATE_EXPIRED

    """ request release of timer thread """

    def release_timer(self):
        self.start_timer()
        self.en_ThState = S4Timer.STATE_RELEASE_REQUEST

    def run(self):
        while True:
            if self.en_ThState == S4Timer.STATE_ACTIVE:
                self.TimeStartTime = time.time()
                while self.en_ThState != S4Timer.STATE_EXPIRED:
                    now = time.time()
                    if (now - self.TimeStartTime) > self.Timeout:
                        self.en_ThState = S4Timer.STATE_EXPIRED
                        if self.Callback is not None:
                            if self.Data is None:
                                self.Callback()
                            else:
                                self.Callback(self.Data)
                        break
                    time.sleep(.05)
            if self.en_ThState == S4Timer.STATE_RELEASE_REQUEST:
                break
            time.sleep(.05)
