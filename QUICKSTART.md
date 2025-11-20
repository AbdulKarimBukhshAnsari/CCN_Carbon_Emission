# Quick Start Guide - Carbon Emission Monitor

## Step-by-Step Instructions for WSL2 Ubuntu

### Step 1: Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-psutil python3-prettytable
```

### Step 2: Navigate to Project
```bash
cd /mnt/d/wahab_ccn
```

### Step 3: Run the Monitor
```bash
python3 pycode/main_psutil.py
```

That's it! The monitor will start showing real-time carbon emissions.

### Step 4: Stop the Monitor
Press `Ctrl+C` to stop monitoring.

---

## What You'll See

The output shows:
- **PID**: Process ID
- **CPU Time**: How long the process has used the CPU
- **Packets**: Estimated network activity
- **Energy**: Energy consumed in Joules
- **Carbon**: CO2 emissions in grams

### Example Output:
```
+------+---------------+---------+-------------+----------------+
| PID  | CPU Time (ms) | Packets |  Energy (J) | Carbon (g CO2) |
+------+---------------+---------+-------------+----------------+
| 1626 |    71480.00   |  127937 | 1084.993700 |    0.143159    |
| 609  |    33340.00   |  138114 |  513.911400 |    0.067808    |
+------+---------------+---------+-------------+----------------+

📊 Total Energy: 2294.282100 J
🌍 Total Carbon: 0.302718 g CO2
```

---

## Troubleshooting

### Error: "No module named 'psutil'"
```bash
sudo apt-get install python3-psutil
```

### Error: "No module named 'prettytable'"
```bash
sudo apt-get install python3-prettytable
```

---

## Next Steps

1. **Monitor for a few minutes** to see which processes use the most energy
2. **Close unnecessary applications** to reduce carbon emissions
3. **Check README.md** for detailed documentation
4. **Optimize your workflow** based on the insights

---

## Quick Commands

```bash
# Install dependencies
sudo apt-get install -y python3-psutil python3-prettytable

# Run monitor
python3 pycode/main_psutil.py

# Stop monitor
# Press Ctrl+C
```

---

**Note**: This version works perfectly on WSL2 without any kernel modifications!
