# Step-by-Step Guide: Running eBPF Kernel Version from Scratch

## ⚠️ IMPORTANT: Check Your Environment First

### Step 1: Verify Your System

```bash
# Check if you're on WSL2 or Native Linux
uname -a
```

**If output contains "microsoft" or "WSL2":**
- ❌ You are on WSL2 - eBPF won't work without major effort
- ✅ **Use the Psutil version instead**: `python3 pycode/main_interactive.py`
- **Skip to "WSL2 Alternative" section below**

**If output is pure Linux (Ubuntu, Debian, etc.):**
- ✅ Continue with eBPF installation below

---

## 🔥 For Native Linux - eBPF Installation

### Step 2: Check Kernel Version

```bash
# Check your kernel version
uname -r

# Example output: 5.15.0-91-generic
```

**Requirement**: Kernel version should be **4.18 or higher** for eBPF support.

---

### Step 3: Install BCC (BPF Compiler Collection)

```bash
# Update package list
sudo apt-get update

# Install BCC tools and Python bindings
sudo apt-get install -y python3-bpfcc bpfcc-tools

# Verify installation
dpkg -l | grep bpfcc
```

**Expected output:**
```
ii  bpfcc-tools           0.xx.x    all    tools for BPF Compiler Collection
ii  python3-bpfcc         0.xx.x    all    Python 3 wrappers for BPF Compiler Collection
```

---

### Step 4: Install Kernel Headers

This is **CRITICAL** - eBPF programs need kernel headers to compile.

```bash
# Install kernel headers matching YOUR kernel version
sudo apt-get install -y linux-headers-$(uname -r)

# Verify installation
ls /lib/modules/$(uname -r)/build
```

**Expected output:**
```
Makefile  arch/  include/  scripts/  ...
```

**If directory doesn't exist:**
```bash
# Try generic headers
sudo apt-get install -y linux-headers-generic

# Or install build essentials
sudo apt-get install -y build-essential
```

---

### Step 5: Install Python Dependencies

```bash
# Install required Python packages
sudo apt-get install -y python3-psutil python3-prettytable

# Optional: For visualizations
sudo apt-get install -y python3-matplotlib

# Optional: For CPU limiting strategy
sudo apt-get install -y cpulimit
```

---

### Step 6: Navigate to Project Directory

```bash
# Go to your project folder
cd /mnt/d/wahab_ccn

# OR if you cloned from git
cd /path/to/CCN_Carbon_Emission
```

---

### Step 7: Verify eBPF Files Exist

```bash
# Check if eBPF programs are present
ls -la eBPF/

# You should see:
# - cpu_monitor.c
# - net_monitor.c
```

---

### Step 8: Test BCC Import (Critical Test)

```bash
# Test if BCC can be imported
sudo python3 -c "
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from bcc import BPF
print('✅ BCC import successful!')
"
```

**Expected output:**
```
✅ BCC import successful!
```

**If you get an error:**
- Check if python3-bpfcc is installed: `dpkg -l | grep python3-bpfcc`
- Reinstall: `sudo apt-get install --reinstall python3-bpfcc`

---

### Step 9: Test eBPF Program Compilation

```bash
# Test if eBPF programs can compile
sudo python3 -c "
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from bcc import BPF

print('Loading CPU monitor...')
bpf = BPF(src_file='eBPF/cpu_monitor.c')
print('✅ CPU monitor compiled successfully!')

print('Loading Network monitor...')
bpf_net = BPF(src_file='eBPF/net_monitor.c')
print('✅ Network monitor compiled successfully!')

print('✅ All eBPF programs working!')
"
```

**If you see errors about kernel headers:**
```
chdir(/lib/modules/5.xx.xx/build): No such file or directory
```

**Fix:**
```bash
# Install the exact kernel headers
sudo apt-get install linux-headers-$(uname -r)

# OR create symlink if headers exist elsewhere
sudo ln -s /usr/src/linux-headers-$(uname -r) /lib/modules/$(uname -r)/build
```

---

### Step 10: Run the eBPF Interactive Monitor

```bash
# Make the script executable (if not already)
chmod +x run_ebpf.sh

# Run the eBPF interactive monitor
sudo ./run_ebpf.sh
```

**OR run directly:**

```bash
# Run the Python script directly
sudo python3 pycode/main_ebpf_interactive.py
```

---

### Step 11: Use the Interactive System

Once running, you'll see:

```
🌍 CARBON EMISSION MONITOR (eBPF Edition)
======================================================================
Kernel-level monitoring using eBPF for maximum accuracy.

📡 Loading eBPF programs...
   Loading CPU monitor (eBPF/cpu_monitor.c)...
   ✅ CPU monitor loaded
   Loading Network monitor (eBPF/net_monitor.c)...
   ✅ Network monitor loaded

📊 Step 1: Collecting baseline metrics...
   (Monitoring with eBPF for 5 seconds...)
```

**Follow the prompts:**
1. Wait for initial monitoring (5 seconds)
2. Review top carbon emitters
3. Choose a mitigation strategy (1-5)
4. Specify how many processes to target
5. Wait for strategy to take effect
6. View before/after comparison
7. See carbon savings!

---

## 🐧 WSL2 Alternative (If eBPF Doesn't Work)

### For WSL2 Users - Use Psutil Version

```bash
# Install dependencies (no kernel headers needed!)
sudo apt-get update
sudo apt-get install -y python3-psutil python3-prettytable

# Optional
sudo apt-get install -y python3-matplotlib cpulimit

# Run the interactive monitor (NO SUDO needed for monitoring)
python3 pycode/main_interactive.py

# OR use the helper script
chmod +x run_interactive.sh
./run_interactive.sh
```

**This version:**
- ✅ Works on WSL2
- ✅ No kernel modifications needed
- ✅ Same features and mitigation strategies
- ✅ Same before/after comparison

---

## 🔍 Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'bcc'"

**Solution:**
```bash
sudo apt-get install --reinstall python3-bpfcc
```

### Issue 2: "Failed to compile BPF module"

**Cause:** Kernel headers missing

**Solution:**
```bash
# Install kernel headers
sudo apt-get install linux-headers-$(uname -r)

# Verify
ls /lib/modules/$(uname -r)/build
```

### Issue 3: "Operation not permitted"

**Cause:** Not running as root

**Solution:**
```bash
# Always use sudo for eBPF version
sudo python3 pycode/main_ebpf_interactive.py
```

### Issue 4: "No such file or directory: eBPF/cpu_monitor.c"

**Cause:** Wrong directory

**Solution:**
```bash
# Make sure you're in the project root
cd /mnt/d/wahab_ccn
pwd  # Should show /mnt/d/wahab_ccn
ls eBPF/  # Should list .c files
```

### Issue 5: On WSL2 - "Module kheaders not found"

**This is NORMAL on WSL2.**

**Solution:**
```bash
# Use psutil version instead
python3 pycode/main_interactive.py
```

---

## 📋 Quick Command Reference

### Check System
```bash
uname -a                          # Check if WSL2 or native Linux
uname -r                          # Check kernel version
dpkg -l | grep bpfcc              # Check if BCC installed
ls /lib/modules/$(uname -r)/build # Check kernel headers
```

### Install Everything (Native Linux)
```bash
sudo apt-get update
sudo apt-get install -y python3-bpfcc bpfcc-tools
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y python3-psutil python3-prettytable python3-matplotlib
sudo apt-get install -y cpulimit
```

### Run eBPF Version
```bash
cd /mnt/d/wahab_ccn
sudo ./run_ebpf.sh
# OR
sudo python3 pycode/main_ebpf_interactive.py
```

### Run Psutil Version (WSL2)
```bash
cd /mnt/d/wahab_ccn
./run_interactive.sh
# OR
python3 pycode/main_interactive.py
```

---

## ✅ Success Checklist

Before running, make sure:

- [ ] On native Linux (not WSL2) for eBPF version
- [ ] Kernel version 4.18+ (`uname -r`)
- [ ] BCC installed (`dpkg -l | grep python3-bpfcc`)
- [ ] Kernel headers installed (`ls /lib/modules/$(uname -r)/build`)
- [ ] Python dependencies installed
- [ ] In project directory (`pwd` shows `/mnt/d/wahab_ccn`)
- [ ] Running with sudo (`sudo python3 ...`)

---

## 🎯 Expected Results

**When it works, you'll see:**

```
🔥 Top 10 Carbon Emitters:
+------+-----+---------------+-------------+----------------+
| Rank | PID | Process Name  | Energy (J)  | Carbon (g CO2) |
+------+-----+---------------+-------------+----------------+
|  1   | 1234| node          | 943.340200  | 0.124468       |
|  2   | 5678| python3       | 474.698200  | 0.062634       |
+------+-----+---------------+-------------+----------------+

📊 Total Energy (Before): 2294.282100 J
🌍 Total Carbon (Before): 0.302718 g CO2

[Apply strategy]

💰 SAVINGS SUMMARY
⚡ Energy Saved: 1083.962100 J (47.24% reduction)
🌱 Carbon Saved: 0.142982 g CO2 (47.24% reduction)
```

---

## 📞 Still Having Issues?

1. **Check README_RESEARCH.md** for academic details
2. **Check EBPF_VS_PSUTIL.md** for version comparison
3. **Use WSL2 version** if eBPF doesn't work
4. **Read error messages carefully** - they usually tell you what's missing

---

**Remember: If you're on WSL2, save yourself time and use the Psutil version! It has the same features and works perfectly.** 🚀
