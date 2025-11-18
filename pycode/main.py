from bcc import BPF
from python.energy_calc import estimate_energy, estimate_carbon
from python.display import display_table
from python.mitigation import apply_mitigation
import time

# Load eBPF programs
bpf_cpu = BPF(src_file="eBPF/cpu_monitor.c")
bpf_cpu.attach_kprobe(event="finish_task_switch", fn_name="trace_sched_switch")

bpf_net = BPF(src_file="eBPF/net_monitor.c")
bpf_net.attach_kprobe(event="ip_rcv", fn_name="trace_packet")  # example hook

cpu_map = bpf_cpu["cpu_usage"]
net_map = bpf_net["packet_count"]

while True:
    metrics = []
    for pid, cpu_time in cpu_map.items():
        packets = net_map.get(pid, 0)
        energy = estimate_energy(cpu_time.value, packets.value if packets else 0)
        carbon = estimate_carbon(energy)
        metrics.append((pid.value, cpu_time.value, packets.value if packets else 0, energy, carbon))
    
    display_table(metrics)
    apply_mitigation(metrics)
    time.sleep(2)
