#ifndef _ISMU_TABLES_P4_
#define _ISMU_TABLES_P4_

// ======================================================
// REGISTERS (STATEFUL MEMORY)
// ======================================================

// Per-flow packet counter
register<bit<32>>(1024) flow_counter;

// Per-flow byte counter
register<bit<32>>(1024) byte_counter;

// Track last destination port (for simple scan heuristic)
register<bit<16>>(1024) last_dst_port;

// ======================================================
// ACTIONS
// ======================================================

// ----------------------
// Forwarding
// ----------------------
action ipv4_forward(bit<48> dstAddr, bit<9> port) {
    hdr.ethernet.dstAddr = dstAddr;
    standard_metadata.egress_spec = port;
}

// ----------------------
// Drop
// ----------------------
action drop() {
    mark_to_drop();
}

// ----------------------
// Mark attack and send to controller
// ----------------------
action mark_attack() {
    meta.is_attack = 1;
    standard_metadata.egress_spec = CPU_PORT;
}

// ----------------------
// Mark DoS
// ----------------------
action mark_dos() {
    meta.is_dos = 1;
    meta.is_attack = 1;
    standard_metadata.egress_spec = CPU_PORT;
}

// ----------------------
// Mark Scan
// ----------------------
action mark_scan() {
    meta.is_scan = 1;
    meta.is_attack = 1;
    standard_metadata.egress_spec = CPU_PORT;
}

// ----------------------
// No action
// ----------------------
action NoAction() {}

// ======================================================
// TABLES
// ======================================================

// ----------------------
// IPv4 Forwarding Table
// ----------------------
table ipv4_lpm {
    key = {
        hdr.ipv4.dstAddr: lpm;
    }
    actions = {
        ipv4_forward;
        drop;
        NoAction;
    }
    size = 2048;
    default_action = drop();
}

// ----------------------
// Rule-based Detection Table
// (Controller can insert rules dynamically)
// ----------------------
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

// ----------------------
// Port-based Scan Detection Table
// (Optional override)
// ----------------------
table scan_table {
    key = {
        meta.src_port: exact;
        meta.dst_port: exact;
    }
    actions = {
        mark_scan;
        NoAction;
    }
    size = 1024;
    default_action = NoAction();
}

// ======================================================
// HELPER FUNCTIONS (INLINE LOGIC)
// ======================================================

// Update flow counters
action update_flow_stats(bit<32> index) {
    bit<32> pkt;
    bit<32> bytes;

    flow_counter.read(pkt, index);
    byte_counter.read(bytes, index);

    pkt = pkt + 1;
    bytes = bytes + standard_metadata.packet_length;

    flow_counter.write(index, pkt);
    byte_counter.write(index, bytes);

    meta.pkt_count = pkt;
    meta.byte_count = bytes;
}

// Simple scan detection using port change heuristic
action detect_scan(bit<32> index) {
    bit<16> prev_port;

    last_dst_port.read(prev_port, index);

    if (meta.dst_port != prev_port) {
        meta.is_scan = 1;
    }

    last_dst_port.write(index, meta.dst_port);
}

// ======================================================
// APPLY BLOCK LOGIC (CALLED FROM INGRESS)
// ======================================================

action apply_detection(bit<32> index) {

    // Update stats
    update_flow_stats(index);

    // DoS detection (threshold)
    if (meta.pkt_count > 500) {
        mark_dos();
        return;
    }

    // Scan detection (port variation)
    detect_scan(index);

    if (meta.is_scan == 1) {
        mark_scan();
        return;
    }

    // Rule-based detection
    detection_table.apply();
}

#endif