import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    matthews_corrcoef
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
# METRICS
# ======================================================

def compute_metrics(y_true, y_pred, y_probs):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)

    auc = roc_auc_score(y_true, y_probs)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    fpr = fp / (fp + tn + 1e-8)
    fnr = fn / (fn + tp + 1e-8)

    return {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1": f1,
        "AUC": auc,
        "FPR": fpr,
        "FNR": fnr,
        "MCC": mcc
    }


# ======================================================
# INFERENCE
# ======================================================

def run_inference(model, X):
    preds = []
    probs = []

    with torch.no_grad():
        for i in range(len(X)):
            x = torch.tensor(X[i], dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(DEVICE)

            logits, _ = model(x)
            prob = torch.softmax(logits, dim=1)

            pred = torch.argmax(prob, dim=1).item()

            preds.append(pred)
            probs.append(prob[:, 1].item())  # probability of attack

    return np.array(preds), np.array(probs)


# ======================================================
# EXPERIMENT RUNNER
# ======================================================

def evaluate_dataset(name, loader):
    print(f"\n===== {name} =====")

    X, y = loader.get_features_labels()

    # Binary conversion (ensure labels are 0/1)
    y = (y > 0).astype(int)

    model = load_model(input_dim=X.shape[1], num_classes=2)

    y_pred, y_probs = run_inference(model, X)

    metrics = compute_metrics(y, y_pred, y_probs)

    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    return metrics


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    results = {}

    # CIC-IoT
    results["CIC-IoT-2023"] = evaluate_dataset(
        "CIC-IoT-2023",
        CICIoTLoader("data/processed/cic_iot.csv")
    )

    # UNSW
    results["UNSW-NB15"] = evaluate_dataset(
        "UNSW-NB15",
        UNSWLoader("data/processed/unsw.csv")
    )

    # ToN-IoT
    results["ToN-IoT"] = evaluate_dataset(
        "ToN-IoT",
        ToNIoTLoader("data/processed/ton_iot.csv")
    )

    print("\n===== SUMMARY TABLE =====")

    for dataset, metrics in results.items():
        print(f"\n{dataset}")
        for k, v in metrics.items():
            print(f"{k}: {v:.4f}")