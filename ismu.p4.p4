#include <core.p4>
#include <v1model.p4>

// ======================================================
// HEADERS
// ======================================================

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  tos;
    bit<16> totalLen;
    bit<16> id;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

// ======================================================
// METADATA
// ======================================================

struct metadata {
    bit<32> flow_hash;
    bit<32> pkt_count;
    bit<1>  is_attack;
}

// ======================================================
// STRUCTS
// ======================================================

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
}

// ======================================================
// REGISTERS (STATEFUL MEMORY)
// ======================================================

// Per-flow packet counter
register<bit<32>>(1024) flow_counter;

// ======================================================
// ACTIONS
// ======================================================

// Forwarding action
action ipv4_forward(bit<48> dstAddr, bit<9> port) {
    hdr.ethernet.dstAddr = dstAddr;
    standard_metadata.egress_spec = port;
}

// Drop action
action drop() {
    mark_to_drop();
}

// Mark attack + send to controller
action mark_attack() {
    meta.is_attack = 1;

    // Send packet to CPU (controller)
    standard_metadata.egress_spec =  CPU_PORT;
}

// No action
action NoAction() {}

// ======================================================
// TABLES
// ======================================================

// LPM forwarding table
table ipv4_lpm {
    key = {
        hdr.ipv4.dstAddr: lpm;
    }
    actions = {
        ipv4_forward;
        drop;
        NoAction;
    }
    size = 1024;
    default_action = drop();
}

// Detection table (optional rule-based override)
table detection_table {
    key = {
        hdr.ipv4.srcAddr: exact;
    }
    actions = {
        mark_attack;
        NoAction;
    }
    size = 1024;
    default_action = NoAction();
}

// ======================================================
// PARSER
// ======================================================

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

// ======================================================
// INGRESS PIPELINE (CORE LOGIC)
// ======================================================

control Ingress(inout headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    apply {

        if (hdr.ipv4.isValid()) {

            // -------------------------------
            // FLOW HASH (simple index)
            // -------------------------------
            meta.flow_hash = (bit<32>) (hdr.ipv4.srcAddr % 1024);

            // -------------------------------
            // READ COUNTER
            // -------------------------------
            flow_counter.read(meta.pkt_count, meta.flow_hash);

            // -------------------------------
            // UPDATE COUNTER
            // -------------------------------
            meta.pkt_count = meta.pkt_count + 1;
            flow_counter.write(meta.flow_hash, meta.pkt_count);

            // -------------------------------
            // DoS DETECTION (THRESHOLD)
            // -------------------------------
            if (meta.pkt_count > 500) {
                mark_attack();
                return;
            }

            // -------------------------------
            // SCAN DETECTION (TTL heuristic)
            // -------------------------------
            if (hdr.ipv4.ttl < 10) {
                mark_attack();
                return;
            }

            // -------------------------------
            // RULE-BASED DETECTION
            // -------------------------------
            detection_table.apply();

            // -------------------------------
            // NORMAL FORWARDING
            // -------------------------------
            ipv4_lpm.apply();
        }
    }
}

// ======================================================
// EGRESS
// ======================================================

control Egress(inout headers hdr,
               inout metadata meta,
               inout standard_metadata_t standard_metadata) {
    apply { }
}

// ======================================================
// CHECKSUM (ignored for simplicity)
// ======================================================

control VerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control ComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

// ======================================================
// DEPARSER
// ======================================================

control Deparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

// ======================================================
// MAIN
// ======================================================

V1Switch(
    MyParser(),
    VerifyChecksum(),
    Ingress(),
    Egress(),
    ComputeChecksum(),
    Deparser()
) main;