def apply_mitigation(metrics):
    for pid, cpu, packets, energy, carbon in metrics:
        if energy > 100:
            print(f"Throttling PID {pid} to save energy...")
            # Example: use `nice` or `cgroups` to limit CPU (advanced)
