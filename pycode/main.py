#!/usr/bin/env python3
import sys
# Add system BCC path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from bcc import BPF
from energy_calc import estimate_energy, estimate_carbon
from display import display_table
from mitigation import apply_mitigation
import time
import os

# Check if running with sudo
if os.geteuid() != 0:
    print("Error: This script must be run with sudo/root privileges")
    print("Usage: sudo python3 pycode/main.py")
    sys.exit(1)

print("Loading eBPF programs...")

# Load eBPF programs
bpf_cpu = BPF(src_file="eBPF/cpu_monitor.c")
print("✓ CPU monitor loaded")

bpf_net = BPF(src_file="eBPF/net_monitor.c")
print("✓ Network monitor loaded")

cpu_map = bpf_cpu["cpu_usage"]
net_map = bpf_net["packet_count"]

print("\nMonitoring carbon emissions (Press Ctrl+C to stop)...\n")

try:
    while True:
        metrics = []
        for k, v in cpu_map.items():
            pid = k.value
            cpu_time_ns = v.value
            
            # Get packet count for this PID
            packets_key = net_map.Key(pid)
            try:
                packets = net_map[packets_key].value
            except KeyError:
                packets = 0
            
            # Calculate energy and carbon
            energy = estimate_energy(cpu_time_ns, packets)
            carbon = estimate_carbon(energy)
            
            # Only show processes with significant activity
            if cpu_time_ns > 0 or packets > 0:
                metrics.append((pid, cpu_time_ns, packets, energy, carbon))
        
        # Sort by carbon emissions (highest first)
        metrics.sort(key=lambda x: x[4], reverse=True)
        
        # Display top 20 processes
        if metrics:
            display_table(metrics[:20])
            apply_mitigation(metrics)
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\nStopping monitoring...")
    print("Cleaning up...")

