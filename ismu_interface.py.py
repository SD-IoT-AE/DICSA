import socket
import struct
import threading
from scapy.all import Ether, IP, TCP, UDP
import numpy as np


class ISMUInterface:
    """
    Receives packets from P4 switch (CPU_PORT) and converts them
    into feature vectors for TSCE.
    """

    def __init__(self, interface="eth0", callback=None):
        """
        interface: network interface connected to BMv2 CPU port
        callback: function to pass extracted features to controller
        """
        self.interface = interface
        self.callback = callback

    # ======================================================
    # FEATURE EXTRACTION (Aligned with TSCE input)
    # ======================================================
    def extract_features(self, pkt):
        """
        Converts packet into feature vector (size = 12)
        """

        features = []

        # -------- Basic IP features --------
        src_ip = int.from_bytes(pkt[IP].src.encode(), 'little', signed=False) if IP in pkt else 0
        dst_ip = int.from_bytes(pkt[IP].dst.encode(), 'little', signed=False) if IP in pkt else 0
        ttl = pkt[IP].ttl if IP in pkt else 0
        proto = pkt[IP].proto if IP in pkt else 0

        features.extend([src_ip % 100000, dst_ip % 100000, ttl, proto])

        # -------- Transport features --------
        src_port = 0
        dst_port = 0
        flags = 0

        if TCP in pkt:
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
            flags = int(pkt[TCP].flags)

        elif UDP in pkt:
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport

        features.extend([src_port, dst_port, flags])

        # -------- Packet-level features --------
        pkt_len = len(pkt)
        features.append(pkt_len)

        # These will be approximated or extended later via telemetry
        pkt_count = 1
        byte_count = pkt_len
        is_attack_flag = 1  # since packet came from CPU port

        features.extend([pkt_count, byte_count, is_attack_flag])

        # Ensure fixed size (12)
        while len(features) < 12:
            features.append(0)

        return np.array(features[:12], dtype=np.float32)

    # ======================================================
    # PACKET HANDLER
    # ======================================================
    def handle_packet(self, raw_data):
        try:
            pkt = Ether(raw_data)

            if IP not in pkt:
                return

            feature_vector = self.extract_features(pkt)

            flow_id = hash(pkt[IP].src + pkt[IP].dst) % 100000

            attacker_ip = pkt[IP].src

            if self.callback:
                self.callback(feature_vector, flow_id, attacker_ip)

        except Exception as e:
            print(f"[ISMU Interface Error] {e}")

    # ======================================================
    # LISTENER (RAW SOCKET)
    # ======================================================
    def start(self):
        """
        Start sniffing packets from interface
        """
        print(f"[ISMU] Listening on interface: {self.interface}")

        # Use raw socket
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        sock.bind((self.interface, 0))

        while True:
            raw_data, _ = sock.recvfrom(65535)
            self.handle_packet(raw_data)

    # ======================================================
    # THREAD WRAPPER
    # ======================================================
    def start_async(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        print("[ISMU] Async listener started")