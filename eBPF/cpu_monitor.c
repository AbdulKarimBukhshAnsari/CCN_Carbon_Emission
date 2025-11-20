#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// Hash maps to store CPU usage and timing information
BPF_HASH(cpu_usage, u32, u64);          // PID -> total CPU time (ns)
BPF_HASH(start_time, u32, u64);         // PID -> start time (ns)
BPF_HASH(process_count, u32, u64);      // PID -> context switch count

// Tracepoint for scheduler context switches
TRACEPOINT_PROBE(sched, sched_switch) {
    u32 prev_pid = args->prev_pid;
    u32 next_pid = args->next_pid;
    u64 ts = bpf_ktime_get_ns();
    
    // Track time for the process being switched out (prev)
    if (prev_pid != 0) {
        u64 *start_ts = start_time.lookup(&prev_pid);
        if (start_ts) {
            // Calculate time delta since this process was scheduled
            u64 delta = ts - *start_ts;
            
            // Add to total CPU time
            u64 zero = 0;
            u64 *total = cpu_usage.lookup_or_try_init(&prev_pid, &zero);
            if (total) {
                *total += delta;
            }
        }
        
        // Increment context switch counter
        u64 zero_count = 0;
        u64 *count = process_count.lookup_or_try_init(&prev_pid, &zero_count);
        if (count) {
            (*count)++;
        }
    }
    
    // Record start time for process being switched in (next)
    if (next_pid != 0) {
        start_time.update(&next_pid, &ts);
    }
    
    return 0;
}

// Optional: Track process creation for better tracking
TRACEPOINT_PROBE(sched, sched_process_fork) {
    u32 parent_pid = args->parent_pid;
    u32 child_pid = args->child_pid;
    
    // Initialize counters for new process
    u64 zero = 0;
    cpu_usage.update(&child_pid, &zero);
    process_count.update(&child_pid, &zero);
    
    return 0;
}

// Optional: Clean up on process exit
TRACEPOINT_PROBE(sched, sched_process_exit) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    // Don't delete, let Python handle cleanup
    // This way we can still see final stats
    
    return 0;
}
