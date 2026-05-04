import time
import numpy as np
import torch

from controller.modules.tsce.inference import TSCEInference
from controller.modules.arem.enforcement import AREM
from controller.modules.cdcs.sync_manager import CDCS
from controller.modules.tsce.alert_buffer import AlertBuffer


# ======================================================
# CONFIG
# ======================================================

NUM_SAMPLES = 1000
WINDOW_SIZE = 10


# ======================================================
# LATENCY UTILITIES
# ======================================================

def compute_stats(times):
    times = np.array(times)

    return {
        "mean_ms": np.mean(times) * 1000,
        "std_ms": np.std(times) * 1000,
        "p50_ms": np.percentile(times, 50) * 1000,
        "p95_ms": np.percentile(times, 95) * 1000,
        "p99_ms": np.percentile(times, 99) * 1000,
        "min_ms": np.min(times) * 1000,
        "max_ms": np.max(times) * 1000,
    }


def print_stats(title, stats):
    print(f"\n===== {title} =====")
    for k, v in stats.items():
        print(f"{k}: {v:.3f}")


# ======================================================
# TSCE LATENCY
# ======================================================

def measure_tsce_latency(tsce):
    times = []

    for _ in range(NUM_SAMPLES):
        sequence = np.random.rand(WINDOW_SIZE, 12)

        start = time.perf_counter()
        tsce.predict(sequence)
        end = time.perf_counter()

        times.append(end - start)

    return compute_stats(times)


# ======================================================
# END-TO-END PIPELINE LATENCY
# ======================================================

def measure_pipeline_latency(tsce, arem, cdcs):
    times = []

    buffer = AlertBuffer(WINDOW_SIZE)

    for i in range(NUM_SAMPLES):

        feature = np.random.rand(12)
        buffer.add(feature)

        if not buffer.is_ready():
            continue

        sequence = buffer.get_sequence()

        start = time.perf_counter()

        # TSCE
        result = tsce.predict(sequence)
        conf = result["confidence"]

        # AREM
        rule = arem.enforce(i, f"10.0.0.{i%5}", conf)

        # CDCS
        cdcs.sync_attack(f"10.0.0.{i%5}", conf, rule["action"])

        end = time.perf_counter()

        times.append(end - start)

        buffer.reset()

    return compute_stats(times)


# ======================================================
# THROUGHPUT
# ======================================================

def measure_throughput(tsce):
    start = time.time()

    count = 0

    for _ in range(NUM_SAMPLES):
        sequence = np.random.rand(WINDOW_SIZE, 12)
        tsce.predict(sequence)
        count += 1

    end = time.time()

    duration = end - start
    throughput = count / duration

    return throughput


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    print("Initializing modules...")

    tsce = TSCEInference()
    arem = AREM()
    cdcs = CDCS()

    # --------------------------------------------------
    # TSCE Latency
    # --------------------------------------------------
    tsce_stats = measure_tsce_latency(tsce)
    print_stats("TSCE Inference Latency (ms)", tsce_stats)

    # --------------------------------------------------
    # End-to-End Pipeline
    # --------------------------------------------------
    pipeline_stats = measure_pipeline_latency(tsce, arem, cdcs)
    print_stats("End-to-End Pipeline Latency (ms)", pipeline_stats)

    # --------------------------------------------------
    # Throughput
    # --------------------------------------------------
    throughput = measure_throughput(tsce)
    print(f"\n===== Throughput =====")
    print(f"Events/sec: {throughput:.2f}")