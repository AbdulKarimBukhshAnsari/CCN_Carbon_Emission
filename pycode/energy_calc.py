def estimate_energy(cpu_time, packets):
    base_cpu_power = 50  # Watts per CPU
    packet_energy_factor = 0.01  # Joules per packet
    energy = base_cpu_power * (cpu_time / 1000) + packet_energy_factor * packets
    return energy

def estimate_carbon(energy):
    return energy * 0.000475  # kg CO2 per joule
