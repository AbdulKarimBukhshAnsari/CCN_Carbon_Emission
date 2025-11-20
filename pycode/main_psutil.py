#!/usr/bin/env python3
"""
Carbon Emission Monitor (WSL2-Compatible Version)
Uses psutil instead of eBPF for WSL2 compatibility
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import psutil
import time
from energy_calc import estimate_energy, estimate_carbon
from display import display_table
from mitigation import apply_mitigation

print("🌍 Carbon Emission Monitor (WSL2-Compatible)")
print("=" * 50)
print("Monitoring system processes for carbon emissions...")
print("Press Ctrl+C to stop\n")

# Track cumulative CPU time
process_data = {}

try:
    while True:
        metrics = []
        
        # Get all running processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_times', 'num_ctx_switches']):
            try:
                pid = proc.info['pid']
                cpu_times = proc.info['cpu_times']
                
                if cpu_times is None:
                    continue
                
                # Calculate CPU time in nanoseconds (user + system time)
                cpu_time_s = cpu_times.user + cpu_times.system
                cpu_time_ns = int(cpu_time_s * 1_000_000_000)
                
                # Estimate network activity from context switches (rough approximation)
                # More context switches often correlate with I/O operations
                ctx_switches = proc.info['num_ctx_switches']
                if ctx_switches:
                    packets_estimate = ctx_switches.voluntary + ctx_switches.involuntary
                else:
                    packets_estimate = 0
                
                # Only track processes with significant activity
                if cpu_time_ns > 100_000_000:  # > 100ms
                    energy = estimate_energy(cpu_time_ns, packets_estimate)
                    carbon = estimate_carbon(energy)
                    
                    metrics.append((pid, cpu_time_ns, packets_estimate, energy, carbon))
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by carbon emissions (highest first)
        metrics.sort(key=lambda x: x[4], reverse=True)
        
        # Display top 20 processes
        if metrics:
            display_table(metrics[:20])
            apply_mitigation(metrics[:20])
        else:
            print("No significant process activity detected...")
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\n✓ Monitoring stopped")
    print("Session complete.")
