import time

_author_ = "int_soumen"
_date_ = "2019-Jan-17"


class HotFlag:
    def __init__(self, cool_down_time_sec):
        self._cool_down_threshold = 5  # sec
        self._cool_down_time = cool_down_time_sec - self._cool_down_threshold
        self._last_burn_time = time.time() - cool_down_time_sec
        pass

    def burn(self):
        self._last_burn_time = time.time()
        pass

    def is_hot(self):
        now = time.time()
        return (now - self._last_burn_time) < self._cool_down_time
        pass
