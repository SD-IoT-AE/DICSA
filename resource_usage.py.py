import time
import psutil
import threading
import numpy as np
import os

try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
except:
    GPU_AVAILABLE = False


# ======================================================
# CONFIG
# ======================================================

MONITOR_DURATION = 30  # seconds
INTERVAL = 0.5         # sampling interval (seconds)


# ======================================================
# RESOURCE MONITOR
# ======================================================

class ResourceMonitor:

    def __init__(self, pid=None):
        self.pid = pid if pid else os.getpid()
        self.process = psutil.Process(self.pid)

        self.cpu_usage = []
        self.memory_usage = []
        self.timestamps = []

        self.gpu_usage = [] if GPU_AVAILABLE else None

        self.running = False

    def sample(self):
        while self.running:
            try:
                cpu = self.process.cpu_percent(interval=None)
                mem = self.process.memory_percent()

                self.cpu_usage.append(cpu)
                self.memory_usage.append(mem)
                self.timestamps.append(time.time())

                # GPU monitoring (if available)
                if GPU_AVAILABLE:
                    gpu_mem = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
                    self.gpu_usage.append(gpu_mem)

            except Exception as e:
                print(f"[Monitor Error] {e}")

            time.sleep(INTERVAL)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.sample, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def get_stats(self):
        stats = {}

        stats["cpu_mean"] = np.mean(self.cpu_usage)
        stats["cpu_max"] = np.max(self.cpu_usage)

        stats["memory_mean"] = np.mean(self.memory_usage)
        stats["memory_max"] = np.max(self.memory_usage)

        if GPU_AVAILABLE and self.gpu_usage:
            stats["gpu_mem_mean_MB"] = np.mean(self.gpu_usage)
            stats["gpu_mem_max_MB"] = np.max(self.gpu_usage)

        return stats


# ======================================================
# SIMULATED WORKLOAD (PIPELINE)
# ======================================================

def simulate_workload():
    """
    Simulates DICSA pipeline load
    Replace with real controller if needed
    """
    for _ in range(2000):
        x = np.random.rand(100, 100)
        _ = np.dot(x, x)  # CPU load

        if GPU_AVAILABLE:
            t = torch.rand(512, 512).cuda()
            _ = torch.matmul(t, t)

        time.sleep(0.01)


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    print("Starting resource monitoring...")

    monitor = ResourceMonitor()
    monitor.start()

    start_time = time.time()

    # Run workload during monitoring window
    while time.time() - start_time < MONITOR_DURATION:
        simulate_workload()

    monitor.stop()

    stats = monitor.get_stats()

    print("\n===== RESOURCE USAGE RESULTS =====")

    print(f"CPU Mean Usage (%): {stats['cpu_mean']:.2f}")
    print(f"CPU Peak Usage (%): {stats['cpu_max']:.2f}")

    print(f"Memory Mean Usage (%): {stats['memory_mean']:.2f}")
    print(f"Memory Peak Usage (%): {stats['memory_max']:.2f}")

    if GPU_AVAILABLE:
        print(f"GPU Memory Mean (MB): {stats['gpu_mem_mean_MB']:.2f}")
        print(f"GPU Memory Peak (MB): {stats['gpu_mem_max_MB']:.2f}")

    print("\nMonitoring complete.")