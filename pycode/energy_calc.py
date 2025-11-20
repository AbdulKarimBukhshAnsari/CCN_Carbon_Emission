def estimate_energy(cpu_time_ns, packets):
    """
    Calculate energy consumption based on CPU time and network packets.
    
    Args:
        cpu_time_ns: CPU time in nanoseconds
        packets: Number of network packets
    
    Returns:
        Energy in Joules
    """
    # Convert nanoseconds to seconds
    cpu_time_s = cpu_time_ns / 1_000_000_000
    
    # Average CPU power consumption: ~15W per core (conservative estimate)
    cpu_power_watts = 15
    
    # Energy from CPU: Power (W) * Time (s) = Joules
    cpu_energy = cpu_power_watts * cpu_time_s
    
    # Network packet energy: ~0.0001 Joules per packet (conservative)
    packet_energy_per_packet = 0.0001
    packet_energy = packet_energy_per_packet * packets
    
    total_energy = cpu_energy + packet_energy
    return total_energy

def estimate_carbon(energy_joules):
    """
    Estimate carbon emissions from energy consumption.
    
    Args:
        energy_joules: Energy in Joules
    
    Returns:
        Carbon emissions in grams of CO2
    """
    # Convert Joules to kWh: 1 kWh = 3,600,000 J
    energy_kwh = energy_joules / 3_600_000
    
    # Global average carbon intensity: ~475 grams CO2 per kWh
    # (varies by region, this is a global average)
    carbon_intensity = 475  # grams CO2 per kWh
    
    carbon_grams = energy_kwh * carbon_intensity
    return carbon_grams

