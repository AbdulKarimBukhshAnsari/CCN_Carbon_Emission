#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

// Hash maps for network activity tracking
BPF_HASH(packet_count, u32, u64);       // PID -> total packet count
BPF_HASH(bytes_sent, u32, u64);         // PID -> total bytes sent
BPF_HASH(bytes_received, u32, u64);     // PID -> total bytes received

// Track incoming packets (receive)
TRACEPOINT_PROBE(net, netif_receive_skb) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0) return 0;  // Skip kernel threads
    
    // Increment packet count
    u64 zero = 0;
    u64 *count = packet_count.lookup_or_try_init(&pid, &zero);
    if (count) {
        (*count)++;
    }
    
    // Track bytes received (approximate)
    u32 len = args->len;
    u64 *bytes_rx = bytes_received.lookup_or_try_init(&pid, &zero);
    if (bytes_rx) {
        *bytes_rx += len;
    }
    
    return 0;
}

// Track outgoing packets (transmit)
TRACEPOINT_PROBE(net, net_dev_xmit) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0) return 0;  // Skip kernel threads
    
    // Increment packet count
    u64 zero = 0;
    u64 *count = packet_count.lookup_or_try_init(&pid, &zero);
    if (count) {
        (*count)++;
    }
    
    // Track bytes sent (approximate)
    u32 len = args->len;
    u64 *bytes_tx = bytes_sent.lookup_or_try_init(&pid, &zero);
    if (bytes_tx) {
        *bytes_tx += len;
    }
    
    return 0;
}

// Optional: Track socket creation for better network monitoring
TRACEPOINT_PROBE(sock, inet_sock_set_state) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0) return 0;
    
    // Initialize counters for processes doing network I/O
    u64 zero = 0;
    packet_count.lookup_or_try_init(&pid, &zero);
    bytes_sent.lookup_or_try_init(&pid, &zero);
    bytes_received.lookup_or_try_init(&pid, &zero);
    
    return 0;
}
