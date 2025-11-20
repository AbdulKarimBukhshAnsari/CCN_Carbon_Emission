import os
import psutil

def apply_mitigation(metrics):
    """
    Apply mitigation strategies for high-emission processes.
    
    Args:
        metrics: List of tuples (pid, cpu_time_ns, packets, energy_j, carbon_g)
    """
    # Energy threshold in Joules (e.g., 1 Joule)
    energy_threshold = 1.0
    
    high_emission_processes = []
    
    for pid, cpu_time_ns, packets, energy, carbon in metrics:
        if energy > energy_threshold:
            high_emission_processes.append((pid, energy, carbon))
    
    if high_emission_processes:
        print("\n⚠️  High Emission Processes Detected:")
        for pid, energy, carbon in high_emission_processes:
            try:
                process = psutil.Process(pid)
                proc_name = process.name()
                print(f"   PID {pid} ({proc_name}): {energy:.4f} J, {carbon:.6f} g CO2")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"   PID {pid}: {energy:.4f} J, {carbon:.6f} g CO2 (process info unavailable)")
        
        print("\n💡 Mitigation Suggestions:")
        print("   • Consider closing unnecessary high-emission processes")
        print("   • Use 'nice' command to lower CPU priority: sudo renice +10 -p <PID>")
        print("   • Monitor and optimize resource-intensive applications")

