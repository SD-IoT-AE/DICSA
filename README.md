# 🚀 DICSA: Distributed In-Plane Cybersecurity Architecture for SDN-IoT

---

## 📌 Overview

**DICSA** is a distributed, real-time cybersecurity framework designed for **Software-Defined Networking (SDN) in IoT environments**. It integrates:

* **In-switch anomaly detection (ISMU)** using P4
* **Temporal-Spatial Correlation Engine (TSCE)** using BiLSTM + Attention
* **Adaptive Response and Enforcement Module (AREM)**
* **Cross-Domain Collaboration System (CDCS)**

The system performs **early-stage detection in the data plane** and **intelligent mitigation in the control plane**, ensuring low latency and high detection accuracy.

---

## 🧠 Architecture

<p align="center">
  <img src="main/architecture.png" width="700"/>
</p>

### Key Components

| Module               | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| **ISMU (P4)**        | Detects anomalies at line-rate using flow counters and heuristics |
| **TSCE (AI Engine)** | Correlates temporal patterns using BiLSTM + Attention             |
| **AREM**             | Applies mitigation policies dynamically                           |
| **CDCS**             | Synchronizes threats across distributed controllers               |

---

## 📂 Repository Structure

```
DICSA/
├── docs/                  # Figures and architecture diagrams
├── data/                  # Dataset loaders and preprocessing
├── p4/                    # Data plane (ISMU)
├── controller/            # Control plane modules
├── models/                # Trained models
├── training/              # Training pipeline
├── experiments/           # Reproducibility scripts
├── visualization/         # Figures generation
├── configs/               # System configurations
├── scripts/               # Execution scripts
```

---

## 📊 Summary of Experimental Results

### 🔹 Binary Classification Performance (%)

| Dataset       | Model | Accuracy  | Precision | Recall | F1    | AUC   | FPR      | FNR      | MCC       |
| ------------- | ----- | --------- | --------- | ------ | ----- | ----- | -------- | -------- | --------- |
| CIC-IoMT-2024 | DICSA | **99.72** | 99.69     | 99.61  | 99.65 | 0.999 | **0.28** | **0.39** | **0.995** |
| CIC-IoT-2023  | DICSA | **99.83** | 99.79     | 99.76  | 99.77 | 0.999 | **0.17** | **0.24** | **0.997** |
| UNSW-NB15     | DICSA | **98.26** | 98.11     | 98.19  | 98.15 | 0.988 | **1.74** | **1.81** | **0.965** |
| ToN-IoT       | DICSA | **99.34** | 99.27     | 99.31  | 99.29 | 0.996 | **0.66** | **0.69** | **0.987** |

---

### 🔹 Key Observations

* Consistently **>99% accuracy** on IoT datasets
* **Lowest FPR/FNR trade-off** among all baselines
* Strong generalization on heterogeneous datasets (UNSW-NB15)
* Near-perfect MCC (~0.99) indicates high prediction reliability

---

## ⚙️ System Requirements

### Software

* Python ≥ 3.8
* P4 Compiler (`p4c`)
* BMv2 (`simple_switch_grpc`)
* Mininet
* pip packages (see below)

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧪 Deployment Instructions (Step-by-Step)

---

### 🔹 Step 1 — Clone Repository

```bash
git clone https://github.com/SD-IoT-AE/DICSA.git
cd DICSA
```

---

### 🔹 Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
pip install scapy psutil seaborn
```

---

### 🔹 Step 3 — Compile P4 Program (ISMU)

```bash
cd p4
chmod +x build.sh
./build.sh
cd ..
```

Expected output:

```
build/ismu.json
build/ismu.p4info.txt
```

---

### 🔹 Step 4 — Start BMv2 Switch

```bash
simple_switch_grpc \
  --device-id 0 \
  --log-console \
  build/ismu.json \
  -- \
  --grpc-server-addr 0.0.0.0:50051
```

---

### 🔹 Step 5 — Load Runtime Rules

```bash
simple_switch_CLI < p4/runtime_config.json
```

---

### 🔹 Step 6 — Start CDCS (Optional Multi-Controller)

```bash
python controller/modules/cdcs/east_west_api.py
```

---

### 🔹 Step 7 — Train TSCE Model

```bash
python training/train_tsce.py
```

Model will be saved in:

```
models/bilstm_attention.pt
```

---

### 🔹 Step 8 — Start Controller

```bash
sudo python controller/main_controller.py
```

---

### 🔹 Step 9 — Start Packet Input (Mininet or Traffic Generator)

Example:

```bash
pingall
iperf
hping3 (for attacks)
```

---

## ▶️ Full Pipeline Execution

```bash
bash scripts/run_full_pipeline.sh
```

---

## 📡 Data Flow (Execution Logic)

1. Packet arrives at switch
2. ISMU detects anomaly → sends to CPU port
3. Controller receives packet (ISMU Interface)
4. TSCE processes sequence
5. AREM decides action
6. CDCS synchronizes across controllers

---

## 📈 Reproducing Paper Results

### Binary Classification

```bash
python experiments/binary_classification.py
```

### Multi-class Classification

```bash
python experiments/multiclass_classification.py
```

### Latency Measurement

```bash
python experiments/latency_measurement.py
```

### Resource Usage

```bash
python experiments/resource_usage.py
```

---

## 📊 Visualization

```bash
python visualization/multi_panel_figures.py
```

Generates:

* Performance comparison plots
* Heatmaps (Figure 10)
* Multi-metric figures

---

## 🧩 Key Features

* ✔ In-network detection (line-rate)
* ✔ AI-based correlation (BiLSTM + Attention)
* ✔ Adaptive mitigation policies
* ✔ Distributed controller synchronization
* ✔ Low latency (< ms-level detection)
* ✔ Scalable to multi-domain SDN

---

## ⚠️ Notes

* Requires **root privileges** for packet capture
* Ensure correct interface (`eth0`, `s1-eth1`, etc.)
* Compatible with **Mininet + BMv2**

---

