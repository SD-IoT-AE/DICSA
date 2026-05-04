import requests
from controller.utils.config_loader import ConfigLoader


class CDCS:

    def __init__(self):
        self.config = ConfigLoader()
        self.peers = self.config.get("cdcs", "peers")
        self.sync_threshold = self.config.get("cdcs", "sync_threshold")

    def should_sync(self, severity):
        return severity >= self.sync_threshold

    def sync_attack(self, attacker_ip, severity, action):

        if not self.should_sync(severity):
            return

        payload = {
            "attacker": attacker_ip,
            "severity": severity,
            "action": action
        }

        for peer in self.peers:
            try:
                requests.post(f"{peer}/sync", json=payload, timeout=1)
                print(f"[CDCS] Synced with {peer}")
            except Exception:
                print(f"[CDCS] Failed to sync with {peer}")