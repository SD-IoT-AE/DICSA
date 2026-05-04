"""
DICSA - P4Runtime Controller
---------------------------
Handles runtime communication with P4 switches.
 - Installs forwarding rules
 - Applies mitigation rules from AREM
 - Reads counters & registers (e.g., from ISMU)
"""

import json
import logging

class P4RuntimeController:
    def __init__(self, device_id=0, grpc_addr="127.0.0.1:50051", p4info_path="p4src/base_forwarding.p4"):
        self.device_id = device_id
        self.grpc_addr = grpc_addr
        self.p4info_path = p4info_path

        # Setup logging
        logging.basicConfig(
            filename="experiments/results_logs/p4runtime.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info(f"Initialized P4RuntimeController for device {self.device_id} at {self.grpc_addr}")

    def load_rules(self, rules_file: str):
        """Load forwarding/mitigation rules from JSON and push them to P4 switch."""
        with open(rules_file, "r") as f:
            rules = json.load(f)

        logging.info(f"Loaded {len(rules)} rules from {rules_file}")
        # TODO: Implement gRPC push of rules to P4 switch
        for rule in rules:
            logging.info(f"Installing rule: {rule}")

    def remove_rule(self, rule_id: str):
        """Remove a specific flow rule."""
        logging.info(f"Removing rule {rule_id}")
        # TODO: implement rule removal

    def read_counters(self):
        """Fetch statistics (packet/byte counters) from switch."""
        logging.info("Reading counters from switch...")
        # TODO: implement counter queries
        return {"packets": 1234, "bytes": 567890}

    def apply_mitigation(self, mitigation_file: str):
        """Load mitigation rules and apply them dynamically."""
        logging.info(f"Applying mitigation rules from {mitigation_file}")
        self.load_rules(mitigation_file)


if __name__ == "__main__":
    controller = P4RuntimeController()
    controller.load_rules("runtime_config/forwarding_rules.json")
    controller.apply_mitigation("runtime_config/mitigation_rules.json")
