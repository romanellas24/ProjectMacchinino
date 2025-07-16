import time


def current_millis():
    return int(time.time() * 1000)


class TimedSwitch:
    def __init__(self, elapse_range_ms):
        self.elapse_range = elapse_range_ms
        self.last_active = current_millis()

    def is_elapse(self):
        now = current_millis()
        if self.last_active + self.elapse_range < now:
            self.last_active = now
            return True
        return False

    def reset(self):
        self.last_active = current_millis()
