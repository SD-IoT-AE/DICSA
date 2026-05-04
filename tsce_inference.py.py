import torch
import numpy as np
from .model import TSCEModel
from controller.utils.config_loader import ConfigLoader


class TSCEInference:

    def __init__(self, model_path="models/bilstm_attention.pt"):
        self.config = ConfigLoader()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = TSCEModel(
            input_dim=self.config.get("tsce", "model", "input_dim"),
            hidden_dim1=self.config.get("tsce", "model", "hidden_dim_1"),
            hidden_dim2=self.config.get("tsce", "model", "hidden_dim_2"),
            num_classes=self.config.get("tsce", "model", "num_classes"),
            dropout=self.config.get("tsce", "training", "dropout")
        ).to(self.device)

        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        self.conf_threshold = self.config.get("tsce", "inference", "confidence_threshold")

    def predict(self, sequence):
        """
        sequence: numpy array (window_size, features)
        """
        x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits, _ = self.model(x)
            probs = torch.softmax(logits, dim=1)

            conf, pred = torch.max(probs, dim=1)

        return {
            "prediction": pred.item(),
            "confidence": conf.item(),
            "probabilities": probs.cpu().numpy().flatten()
        }

    def is_confident(self, confidence):
        return confidence >= self.conf_threshold