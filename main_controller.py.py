import time
import numpy as np

from controller.modules.tsce.inference import TSCEInference
from controller.modules.tsce.alert_buffer import AlertBuffer
from controller.modules.arem.enforcement import AREM
from controller.modules.cdcs.sync_manager import CDCS
from controller.utils.config_loader import ConfigLoader
from controller.utils.logger import setup_logger


class DICSAController:

    def __init__(self):
        self.config = ConfigLoader()
        self.logger = setup_logger()

        self.tsce = TSCEInference()
        self.arem = AREM()
        self.cdcs = CDCS()

        self.buffer = AlertBuffer(
            self.config.get("tsce", "sequence", "window_size")
        )

    def process_ismu_alert(self, feature_vector, flow_id, attacker_ip):

        # Step 1: Add to buffer
        self.buffer.add(feature_vector)

        if not self.buffer.is_ready():
            return

        # Step 2: TSCE inference
        sequence = self.buffer.get_sequence()
        result = self.tsce.predict(sequence)

        pred = result["prediction"]
        conf = result["confidence"]

        self.logger.info(f"Prediction={pred}, Confidence={conf:.4f}")

        # Step 3: Decision
        if self.tsce.is_confident(conf):

            # Step 4: Mitigation
            rule = self.arem.enforce(flow_id, attacker_ip, conf)

            # Step 5: Synchronization
            self.cdcs.sync_attack(attacker_ip, conf, rule["action"])

        # Step 6: Reset buffer (optional sliding)
        self.buffer.reset()

    def simulate_stream(self):
        """
        Simulated ISMU alerts (replace with real P4 input)
        """
        for i in range(100):
            feature_vector = np.random.rand(12)

            self.process_ismu_alert(
                feature_vector,
                flow_id=i,
                attacker_ip=f"10.0.0.{i%5}"
            )

            time.sleep(0.5)


if __name__ == "__main__":
    controller = DICSAController()
    controller.simulate_stream()