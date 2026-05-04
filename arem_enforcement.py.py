import time
from controller.utils.config_loader import ConfigLoader


class AREM:

    def __init__(self):
        self.config = ConfigLoader()

        self.high = self.config.get("arem", "thresholds", "high")
        self.medium = self.config.get("arem", "thresholds", "medium")
        self.expiration = self.config.get("arem", "rules", "expiration_time")

        self.active_rules = {}

    def decide_action(self, severity):
        if severity >= self.high:
            return "DROP"
        elif severity >= self.medium:
            return "RATE_LIMIT"
        else:
            return "MONITOR"

    def enforce(self, flow_id, attacker_ip, severity):

        action = self.decide_action(severity)

        rule = {
            "flow_id": flow_id,
            "attacker": attacker_ip,
            "action": action,
            "installed_at": time.time(),
            "expires_at": time.time() + self.expiration
        }

        self.active_rules[flow_id] = rule

        print(f"[AREM] Enforcing {action} on {attacker_ip}")

        # TODO: integrate with P4Runtime
        return rule

    def cleanup(self):
        now = time.time()
        expired = [fid for fid, r in self.active_rules.items() if r["expires_at"] < now]

        for fid in expired:
            print(f"[AREM] Removing expired rule {fid}")
            del self.active_rules[fid]