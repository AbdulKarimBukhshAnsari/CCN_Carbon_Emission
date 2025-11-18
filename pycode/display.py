from prettytable import PrettyTable

def display_table(metrics):
    table = PrettyTable()
    table.field_names = ["PID", "CPU(ms)", "Packets", "Energy(J)", "Carbon(kg)"]
    for pid, cpu, packets, energy, carbon in metrics:
        table.add_row([pid, cpu, packets, round(energy,2), round(carbon,4)])
    print(table)
