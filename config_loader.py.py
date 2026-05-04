import yaml
import os


class ConfigLoader:
    def __init__(self, config_path="configs/system_config.yaml"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, *keys):
        """
        Access nested config values safely
        Example:
            get("tsce", "training", "batch_size")
        """
        data = self.config
        for key in keys:
            data = data.get(key, None)
            if data is None:
                return None
        return data

    def get_all(self):
        return self.config