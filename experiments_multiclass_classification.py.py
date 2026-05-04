import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report
)

from controller.modules.tsce.model import TSCEModel
from data.loaders.cic_iot_loader import CICIoTLoader
from data.loaders.unsw_loader import UNSWLoader
from data.loaders.ton_iot_loader import ToNIoTLoader


# ======================================================
# CONFIG
# ======================================================

MODEL_PATH = "models/bilstm_attention.pt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ======================================================
# LOAD MODEL
# ======================================================

def load_model(input_dim, num_classes):
    model = TSCEModel(
        input_dim=input_dim,
        hidden_dim1=128,
        hidden_dim2=64,
        num_classes=num_classes,
        dropout=0.3
    ).to(DEVICE)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    return model


# ======================================================
# INFERENCE
# ======================================================

def run_inference(model, X):
    preds = []

    with torch.no_grad():
        for i in range(len(X)):
            x = torch.tensor(X[i], dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(DEVICE)

            logits, _ = model(x)
            pred = torch.argmax(logits, dim=1).item()

            preds.append(pred)

    return np.array(preds)


# ======================================================
# METRICS
# ======================================================

def compute_metrics(y_true, y_pred, class_names=None):

    acc = accuracy_score(y_true, y_pred)

    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")

    macro_prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    macro_rec = recall_score(y_true, y_pred, average="macro", zero_division=0)

    cm = confusion_matrix(y_true, y_pred)

    print("\n=== Overall Metrics ===")
    print(f"Accuracy       : {acc:.4f}")
    print(f"Macro F1       : {macro_f1:.4f}")
    print(f"Weighted F1    : {weighted_f1:.4f}")
    print(f"Macro Precision: {macro_prec:.4f}")
    print(f"Macro Recall   : {macro_rec:.4f}")

    print("\n=== Classification Report ===")
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

    print("\n=== Confusion Matrix ===")
    print(cm)

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "confusion_matrix": cm
    }


# ======================================================
# DATASET EVALUATION
# ======================================================

def evaluate_dataset(name, loader, class_names=None):
    print(f"\n===== {name} (Multi-class) =====")

    X, y = loader.get_features_labels()

    num_classes = len(np.unique(y))

    model = load_model(input_dim=X.shape[1], num_classes=num_classes)

    y_pred = run_inference(model, X)

    results = compute_metrics(y, y_pred, class_names)

    return results


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    results = {}

    # --------------------------------------------------
    # CIC-IoT (example class labels — adjust if needed)
    # --------------------------------------------------
    cic_classes = [
        "Normal",
        "DDoS",
        "DoS",
        "Scan",
        "Bot",
        "BruteForce"
    ]

    results["CIC-IoT-2023"] = evaluate_dataset(
        "CIC-IoT-2023",
        CICIoTLoader("data/processed/cic_iot.csv"),
        cic_classes
    )

    # --------------------------------------------------
    # UNSW-NB15
    # --------------------------------------------------
    unsw_classes = [
        "Normal",
        "Fuzzers",
        "Analysis",
        "Backdoor",
        "DoS",
        "Exploits",
        "Generic",
        "Reconnaissance",
        "Shellcode",
        "Worms"
    ]

    results["UNSW-NB15"] = evaluate_dataset(
        "UNSW-NB15",
        UNSWLoader("data/processed/unsw.csv"),
        unsw_classes
    )

    # --------------------------------------------------
    # ToN-IoT
    # --------------------------------------------------
    ton_classes = [
        "Normal",
        "DDoS",
        "DoS",
        "Scanning",
        "Injection",
        "Backdoor"
    ]

    results["ToN-IoT"] = evaluate_dataset(
        "ToN-IoT",
        ToNIoTLoader("data/processed/ton_iot.csv"),
        ton_classes
    )

    print("\n===== FINAL SUMMARY =====")

    for dataset, res in results.items():
        print(f"\n{dataset}")
        print(f"Accuracy    : {res['accuracy']:.4f}")
        print(f"Macro F1    : {res['macro_f1']:.4f}")
        print(f"Weighted F1 : {res['weighted_f1']:.4f}")