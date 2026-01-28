import time

class CooldownManager:
    def __init__(self, cooldown_seconds=60):
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = {}

    def is_allowed(self, key):
        """
        key can be (zone + action) or person_id
        """
        current_time = time.time()

        if key not in self.last_alert_time:
            self.last_alert_time[key] = current_time
            return True

        elapsed = current_time - self.last_alert_time[key]

        if elapsed >= self.cooldown_seconds:
            self.last_alert_time[key] = current_time
            return True

        return False
