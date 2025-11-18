#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

BPF_HASH(packet_count, u32, u64);

int trace_packet(struct __sk_buff *skb) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    u64 *count = packet_count.lookup(&pid);
    if (count) {
        (*count)++;
        packet_count.update(&pid, count);
    } else {
        u64 initial = 1;
        packet_count.update(&pid, &initial);
    }
    return 0;
}
