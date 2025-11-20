from prettytable import PrettyTable
import os

def display_table(metrics):
    """
    Display process metrics in a formatted table.
    
    Args:
        metrics: List of tuples (pid, cpu_time_ns, packets, energy_j, carbon_g)
    """
    # Clear screen for better readability (optional)
    os.system('clear' if os.name != 'nt' else 'cls')
    
    table = PrettyTable()
    table.field_names = ["PID", "CPU Time (ms)", "Packets", "Energy (J)", "Carbon (g CO2)"]
    
    total_energy = 0
    total_carbon = 0
    
    for pid, cpu_time_ns, packets, energy, carbon in metrics:
        # Convert nanoseconds to milliseconds for display
        cpu_ms = cpu_time_ns / 1_000_000
        
        table.add_row([
            pid, 
            f"{cpu_ms:.2f}", 
            packets, 
            f"{energy:.6f}", 
            f"{carbon:.6f}"
        ])
        
        total_energy += energy
        total_carbon += carbon
    
    print(table)
    print(f"\n📊 Total Energy: {total_energy:.6f} J")
    print(f"🌍 Total Carbon: {total_carbon:.6f} g CO2")
    print(f"💡 Equivalent to: {total_carbon/1000:.9f} kg CO2")

