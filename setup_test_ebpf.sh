#!/bin/bash

# eBPF Setup and Testing Script
# This script will check all prerequisites and guide you through setup

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        eBPF Carbon Monitor - Setup & Test Script            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step 1: Check OS
echo -e "${YELLOW}Step 1: Checking Operating System...${NC}"
if grep -qi microsoft /proc/version; then
    echo -e "${RED}✗ You are on WSL2${NC}"
    echo ""
    echo "WSL2 does not support eBPF without custom kernel compilation."
    echo ""
    echo -e "${GREEN}RECOMMENDATION: Use Psutil version instead${NC}"
    echo "  Run: python3 pycode/main_interactive.py"
    echo ""
    read -p "Do you want to continue anyway? (yes/no): " cont
    if [ "$cont" != "yes" ]; then
        echo "Exiting. Use Psutil version for WSL2."
        exit 0
    fi
else
    echo -e "${GREEN}✓ Running on Native Linux${NC}"
fi
echo ""

# Step 2: Check Kernel Version
echo -e "${YELLOW}Step 2: Checking Kernel Version...${NC}"
KERNEL_VERSION=$(uname -r)
echo "  Kernel: $KERNEL_VERSION"

MAJOR=$(echo $KERNEL_VERSION | cut -d. -f1)
MINOR=$(echo $KERNEL_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 4 ] || ([ "$MAJOR" -eq 4 ] && [ "$MINOR" -lt 18 ]); then
    echo -e "${RED}✗ Kernel version too old (need 4.18+)${NC}"
    echo "  Please upgrade your kernel"
    exit 1
else
    echo -e "${GREEN}✓ Kernel version supports eBPF${NC}"
fi
echo ""

# Step 3: Check if running as root
echo -e "${YELLOW}Step 3: Checking Privileges...${NC}"
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Not running as root${NC}"
    echo ""
    echo "eBPF requires root privileges."
    echo "Please run with sudo:"
    echo "  sudo $0"
    exit 1
else
    echo -e "${GREEN}✓ Running with root privileges${NC}"
fi
echo ""

# Step 4: Check BCC Installation
echo -e "${YELLOW}Step 4: Checking BCC Installation...${NC}"
if dpkg -l | grep -q python3-bpfcc; then
    echo -e "${GREEN}✓ python3-bpfcc installed${NC}"
else
    echo -e "${RED}✗ python3-bpfcc not installed${NC}"
    echo ""
    read -p "Install now? (yes/no): " install_bcc
    if [ "$install_bcc" = "yes" ]; then
        echo "Installing BCC..."
        apt-get update
        apt-get install -y python3-bpfcc bpfcc-tools
    else
        echo "Cannot proceed without BCC. Exiting."
        exit 1
    fi
fi
echo ""

# Step 5: Check Kernel Headers
echo -e "${YELLOW}Step 5: Checking Kernel Headers...${NC}"
if [ -d "/lib/modules/$(uname -r)/build" ]; then
    echo -e "${GREEN}✓ Kernel headers found${NC}"
else
    echo -e "${RED}✗ Kernel headers not found${NC}"
    echo ""
    read -p "Install now? (yes/no): " install_headers
    if [ "$install_headers" = "yes" ]; then
        echo "Installing kernel headers..."
        apt-get install -y linux-headers-$(uname -r)
        
        # Verify again
        if [ -d "/lib/modules/$(uname -r)/build" ]; then
            echo -e "${GREEN}✓ Kernel headers installed successfully${NC}"
        else
            echo -e "${RED}✗ Failed to install kernel headers${NC}"
            echo "You may need to install them manually"
            exit 1
        fi
    else
        echo "Cannot proceed without kernel headers. Exiting."
        exit 1
    fi
fi
echo ""

# Step 6: Check Python Dependencies
echo -e "${YELLOW}Step 6: Checking Python Dependencies...${NC}"

missing_deps=""

if ! python3 -c "import psutil" 2>/dev/null; then
    echo -e "${RED}✗ python3-psutil not installed${NC}"
    missing_deps="$missing_deps python3-psutil"
else
    echo -e "${GREEN}✓ python3-psutil installed${NC}"
fi

if ! python3 -c "import prettytable" 2>/dev/null; then
    echo -e "${RED}✗ python3-prettytable not installed${NC}"
    missing_deps="$missing_deps python3-prettytable"
else
    echo -e "${GREEN}✓ python3-prettytable installed${NC}"
fi

if [ -n "$missing_deps" ]; then
    echo ""
    read -p "Install missing dependencies? (yes/no): " install_deps
    if [ "$install_deps" = "yes" ]; then
        apt-get install -y $missing_deps
    else
        echo "Warning: Missing dependencies may cause errors"
    fi
fi
echo ""

# Step 7: Test BCC Import
echo -e "${YELLOW}Step 7: Testing BCC Import...${NC}"
if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); from bcc import BPF" 2>/dev/null; then
    echo -e "${GREEN}✓ BCC import successful${NC}"
else
    echo -e "${RED}✗ BCC import failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Reinstall: apt-get install --reinstall python3-bpfcc"
    echo "  2. Check: dpkg -l | grep bpfcc"
    exit 1
fi
echo ""

# Step 8: Check eBPF Files
echo -e "${YELLOW}Step 8: Checking eBPF Source Files...${NC}"
if [ -f "eBPF/cpu_monitor.c" ]; then
    echo -e "${GREEN}✓ eBPF/cpu_monitor.c found${NC}"
else
    echo -e "${RED}✗ eBPF/cpu_monitor.c not found${NC}"
    echo "Make sure you're in the project directory"
    exit 1
fi

if [ -f "eBPF/net_monitor.c" ]; then
    echo -e "${GREEN}✓ eBPF/net_monitor.c found${NC}"
else
    echo -e "${RED}✗ eBPF/net_monitor.c not found${NC}"
    exit 1
fi
echo ""

# Step 9: Test eBPF Compilation
echo -e "${YELLOW}Step 9: Testing eBPF Program Compilation...${NC}"
echo "  This may take a few seconds..."

if python3 << 'EOF' 2>&1 | grep -q "SUCCESS"
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
try:
    from bcc import BPF
    bpf_cpu = BPF(src_file="eBPF/cpu_monitor.c")
    bpf_net = BPF(src_file="eBPF/net_monitor.c")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF
then
    echo -e "${GREEN}✓ eBPF programs compiled successfully${NC}"
else
    echo -e "${RED}✗ eBPF compilation failed${NC}"
    echo ""
    echo "Common causes:"
    echo "  - Kernel headers mismatch"
    echo "  - Missing kernel configuration"
    echo "  - Syntax errors in .c files"
    exit 1
fi
echo ""

# All checks passed
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              ✓ ALL CHECKS PASSED!                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}Your system is ready to run eBPF Carbon Monitor!${NC}"
echo ""
echo "Run the interactive monitor with:"
echo -e "${GREEN}  sudo python3 pycode/main_ebpf_interactive.py${NC}"
echo ""
echo "Or use the helper script:"
echo -e "${GREEN}  sudo ./run_ebpf.sh${NC}"
echo ""

read -p "Do you want to run the monitor now? (yes/no): " run_now
if [ "$run_now" = "yes" ]; then
    echo ""
    echo -e "${BLUE}Starting eBPF Carbon Monitor...${NC}"
    echo ""
    python3 pycode/main_ebpf_interactive.py
fi
