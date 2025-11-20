# 🌍 eBPF-based Real-time Energy Monitoring and Mitigation in the Linux Networking Stack

> **Research Project**: Carbon Emission Monitoring using eBPF  
> **Institution**: NED University of Engineering and Technology  
> **Course**: Software Engineering  
> **Team**: SE-23056, SE-23081, SE-23085, SE-230924

---

## 📄 Research Paper

**For complete academic documentation, see [README_RESEARCH.md](README_RESEARCH.md)**

This project implements an eBPF-based solution for real-time monitoring and mitigation of software-origin energy inefficiencies in the Linux networking stack, as described in our research paper.

---

## 🎯 Project Overview

Modern computing infrastructure faces exponential growth in energy consumption due to data traffic, cloud services, and IoT devices. While hardware-level optimizations (Energy-Efficient Ethernet, dynamic voltage scaling) have been extensively studied, **software-level energy inefficiencies** remain largely unexplored.

This project addresses that gap by:
- **Monitoring** CPU utilization and packet-level behaviors in real-time
- **Quantifying** energy waste through power consumption models
- **Mitigating** inefficiencies via adaptive strategies (flow aggregation, packet filtering, rate limiting)
- **Demonstrating** 20-60% carbon reduction without affecting performance

---

## 🌟 Two Implementation Versions

### 🔥 eBPF Version (Native Linux)
- **Kernel-level monitoring** via eBPF tracepoints
- **Ultra-low overhead** (<0.1% CPU)
- **Nanosecond precision** CPU time tracking
- **Real packet counting** from network layer
- **Requires**: Native Linux with kernel headers

### 🐧 Psutil Version (WSL2/Linux)
- **User-space monitoring** using psutil library
- **WSL2 compatible** - no kernel modifications
- **Cross-platform** support
- **Simple installation**
- **Requires**: Python3 with psutil

---

## 🚀 Quick Start

### For Native Linux (eBPF Version)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-bpfcc bpfcc-tools linux-headers-$(uname -r)
sudo apt-get install -y python3-psutil python3-prettytable

# Run eBPF interactive monitor
sudo ./run_ebpf.sh

# Or directly
sudo python3 pycode/main_ebpf_interactive.py
```

### For WSL2/Ubuntu (Psutil Version)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-psutil python3-prettytable

# Run interactive monitor
./run_interactive.sh

# Or directly
python3 pycode/main_interactive.py
```

### Optional: CPU Limiting Support

```bash
sudo apt-get install cpulimit
```

### Optional: Visualization Support

```bash
sudo apt-get install python3-matplotlib
```

--- 📊 How It Works

### Energy Calculation

1. **CPU Energy**: 
   - Power: ~15W per active core
   - Formula: `Energy (J) = Power (W) × Time (s)`

2. **Network Energy**:
   - Energy: ~0.0001 J per packet
   - Formula: `Energy (J) = 0.0001 × Packets`

3. **Carbon Emissions**:
   - Conversion: `1 kWh = 3,600,000 J`
   - Carbon Intensity: ~475g CO2 per kWh (global average)
   - Formula: `Carbon (g CO2) = Energy (kWh) × 475`

### Architecture

```
┌─────────────────────────────────────────┐
│          Process Monitor                │
│  (eBPF/psutil based tracking)           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       Energy Calculator                 │
│  - CPU time → Energy (Joules)           │
│  - Network packets → Energy             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Carbon Estimator                   │
│  Energy → CO2 emissions (grams)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     Display & Mitigation                │
│  - Show top emitters                    │
│  - Suggest optimizations                │
└─────────────────────────────────────────┘
```

## 📁 Project Structure

```
wahab_ccn/
├── README.md                      # This file
├── CEP_DOCUMENTATION.md           # Complete CEP project documentation
├── QUICKSTART.md                  # Quick start guide
├── run_ebpf.sh                    # eBPF version runner (Native Linux)
├── run_interactive.sh             # Psutil version runner (WSL2)
├── run.sh                         # Basic monitor runner
├── requirements.txt               # Python dependencies
│
├── eBPF/                          # eBPF kernel programs
│   ├── cpu_monitor.c              # CPU usage tracking (tracepoints)
│   └── net_monitor.c              # Network packet tracking (tracepoints)
│
└── pycode/                        # Python modules
    ├── main.py                    # Basic eBPF monitor
    ├── main_psutil.py             # Basic psutil monitor (WSL2)
    ├── main_ebpf_interactive.py   # 🔥 INTERACTIVE eBPF VERSION
    ├── main_interactive.py        # 🐧 INTERACTIVE PSUTIL VERSION
    ├── energy_calc.py             # Energy and carbon calculations
    ├── display.py                 # Table formatting
    ├── mitigation.py              # Mitigation suggestions
    ├── reduction_strategies.py    # Real reduction implementations
    ├── comparison.py              # Before/After comparison
    └── visualization.py           # Chart generation
```

---

## 🎮 Usage Examples

### Interactive Mode (Recommended)

**eBPF Version (Native Linux):**
```bash
sudo ./run_ebpf.sh
```

**Psutil Version (WSL2/Linux):**
```bash
./run_interactive.sh
```

### Continuous Monitoring Mode

**eBPF Version:**
```bash
sudo python3 pycode/main.py
```

**Psutil Version:**
```bash
python3 pycode/main_psutil.py
```

--- Sample Output
```
+------+---------------+---------+------------+----------------+
| PID  | CPU Time (ms) | Packets | Energy (J) | Carbon (g CO2) |
+------+---------------+---------+------------+----------------+
| 1626 |    62140.00   |  112402 | 943.340200 |    0.124468    |
| 609  |    30820.00   |  123982 | 474.698200 |    0.062634    |
+------+---------------+---------+------------+----------------+

📊 Total Energy: 2076.414000 J
🌍 Total Carbon: 0.273971 g CO2
💡 Equivalent to: 0.000273971 kg CO2
```

### Applying Mitigation
When high-emission processes are detected, you can:
```bash
# Lower CPU priority of a process
sudo renice +10 -p <PID>

# Monitor specific process
top -p <PID>

# Kill unnecessary process
kill <PID>
```

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'bcc'"
```bash
# Install BCC system-wide
sudo apt-get install python3-bpfcc bpfcc-tools
```

### "Failed to compile BPF module" on WSL2
```bash
# Use the psutil version instead
python3 pycode/main_psutil.py
```

### "No module named 'prettytable'"
```bash
# Install required packages
sudo apt-get install python3-prettytable python3-psutil
```

### Permission Denied
```bash
# Run with sudo for eBPF version
sudo python3 pycode/main.py

# Or use psutil version without sudo
python3 pycode/main_psutil.py
```

## 🌱 Carbon Reduction Tips

1. **Close Idle Applications**: Reduce unnecessary background processes
2. **Optimize Code**: Efficient algorithms = less CPU = less carbon
3. **Use Sleep States**: Let your system idle when not in use
4. **Batch Processing**: Group tasks instead of running continuously
5. **Monitor Regularly**: Track your carbon footprint over time

## 📚 Technical Details

### Why eBPF?
eBPF (extended Berkeley Packet Filter) allows running sandboxed programs in the Linux kernel without changing kernel source code. This provides:
- Low overhead monitoring
- Accurate process-level metrics
- Kernel-level visibility

### Carbon Intensity
The tool uses a global average of 475g CO2/kWh. This varies by region:
- **Coal-heavy regions**: 800-1000g CO2/kWh
- **Renewable-heavy regions**: 50-200g CO2/kWh
- **Global average**: ~475g CO2/kWh

### Limitations
- Network packet estimation is approximate in psutil version
- Carbon intensity is a global average (varies by location)
- Energy calculations are estimates based on typical hardware

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Improve carbon estimation formulas
- Add region-specific carbon intensities

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

Abdul Karim Bukhsh Ansari

## 🙏 Acknowledgments

- BCC (BPF Compiler Collection) project
- psutil library
- Linux kernel eBPF developers

---

**Note**: For WSL2 users, always use `main_psutil.py`. The eBPF version requires a custom-compiled kernel with headers, which is not standard in WSL2.
