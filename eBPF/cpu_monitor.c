#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/ktime.h>
#include <bcc/proto.h>

BPF_HASH(cpu_usage, u32, u64);

int trace_sched_switch(struct pt_regs *ctx, struct task_struct *prev) {
    u32 pid = prev->pid;
    u64 ts = bpf_ktime_get_ns();

    u64 *last_ts = cpu_usage.lookup(&pid);
    if (last_ts) {
        u64 delta = ts - *last_ts;
        cpu_usage.update(&pid, &delta);
    } else {
        cpu_usage.update(&pid, &ts);
    }
    return 0;
}
