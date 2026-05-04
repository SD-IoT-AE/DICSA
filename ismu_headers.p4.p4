#ifndef _ISMU_HEADERS_P4_
#define _ISMU_HEADERS_P4_

// ======================================================
// ETHERNET HEADER
// ======================================================

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

// ======================================================
// IPV4 HEADER (FULL SPEC)
// ======================================================

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  tos;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

// ======================================================
// TCP HEADER (FOR FUTURE EXTENSION / PORT SCAN DETECTION)
// ======================================================

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  reserved;
    bit<9>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

// ======================================================
// UDP HEADER
// ======================================================

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length;
    bit<16> checksum;
}

// ======================================================
// HEADERS STRUCT
// ======================================================

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    tcp_t      tcp;
    udp_t      udp;
}

// ======================================================
// METADATA STRUCT (CORE OF ISMU)
// ======================================================

struct metadata {

    // Flow identification
    bit<32> flow_hash;

    // Traffic statistics
    bit<32> pkt_count;
    bit<32> byte_count;

    // Detection flags
    bit<1>  is_attack;
    bit<1>  is_scan;
    bit<1>  is_dos;

    // Ports (for scan detection)
    bit<16> src_port;
    bit<16> dst_port;

    // Timestamp (for future sliding window logic)
    bit<48> timestamp;
}

// ======================================================
// CONSTANTS
// ======================================================

// BMv2 CPU port (used to send packets to controller)
const bit<9> CPU_PORT = 255;

// Protocol values
const bit<16> ETHERTYPE_IPV4 = 0x0800;
const bit<8>  IP_PROTO_TCP   = 6;
const bit<8>  IP_PROTO_UDP   = 17;

#endif