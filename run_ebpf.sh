#!/bin/bash

# eBPF Carbon Emission Monitor - Interactive Edition
# For Native Linux with eBPF Support

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear

echo -e "${MAGENTA}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🔥 CARBON EMISSION MONITOR - eBPF Edition 🔥           ║"
echo "║                                                                ║"
echo "║            Kernel-Level Carbon Tracking                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}eBPF Features:${NC}"
echo "  • Kernel-level process monitoring"
echo "  • Ultra-low overhead tracking"
echo "  • Accurate CPU time measurement"
echo "  • Real network packet counting"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Error: eBPF requires root privileges${NC}"
    echo ""
    echo "Please run with sudo:"
    echo "  sudo ./run_ebpf.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Running with sudo privileges${NC}"

# Check kernel version
KERNEL_VERSION=$(uname -r)
echo -e "${BLUE}Kernel Version: ${NC}$KERNEL_VERSION"

# Check if on WSL2
if grep -qi microsoft /proc/version; then
    echo -e "${YELLOW}"
    echo "⚠️  WARNING: You are running on WSL2!"
    echo ""
    echo "WSL2 has limited eBPF support and lacks kernel headers."
    echo "This eBPF version may not work properly on WSL2."
    echo ""
    echo "For WSL2, please use:"
    echo "  python3 pycode/main_interactive.py"
    echo ""
    echo -e "${NC}"
    read -p "Continue anyway? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Exiting..."
        exit 0
    fi
fi

# Check BCC installation
echo ""
echo -e "${YELLOW}Checking eBPF/BCC dependencies...${NC}"

if dpkg -l | grep -q python3-bpfcc; then
    echo -e "${GREEN}✓${NC} python3-bpfcc installed"
else
    echo -e "${RED}✗${NC} python3-bpfcc not found"
    echo ""
    echo "Install with:"
    echo "  sudo apt-get install python3-bpfcc bpfcc-tools"
    exit 1
fi

if dpkg -l | grep -q bpfcc-tools; then
    echo -e "${GREEN}✓${NC} bpfcc-tools installed"
else
    echo -e "${YELLOW}!${NC} bpfcc-tools not found (recommended)"
fi

# Check kernel headers
if [ -d "/lib/modules/$(uname -r)/build" ]; then
    echo -e "${GREEN}✓${NC} Kernel headers found"
else
    echo -e "${RED}✗${NC} Kernel headers not found"
    echo ""
    echo "eBPF programs need kernel headers to compile."
    echo "Install with:"
    echo "  sudo apt-get install linux-headers-\$(uname -r)"
    echo ""
    read -p "Continue anyway? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

# Check other dependencies
if python3 -c "import psutil" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-psutil installed"
else
    echo -e "${RED}✗${NC} python3-psutil not found"
    echo "  Install with: sudo apt-get install python3-psutil"
    exit 1
fi

if python3 -c "import prettytable" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-prettytable installed"
else
    echo -e "${RED}✗${NC} python3-prettytable not found"
    echo "  Install with: sudo apt-get install python3-prettytable"
    exit 1
fi

# Check optional dependencies
if command -v cpulimit &> /dev/null; then
    echo -e "${GREEN}✓${NC} cpulimit installed (optional)"
else
    echo -e "${YELLOW}!${NC} cpulimit not found (optional, for CPU limiting)"
fi

if python3 -c "import matplotlib" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-matplotlib installed (optional)"
else
    echo -e "${YELLOW}!${NC} python3-matplotlib not found (optional, for charts)"
fi

echo ""
echo -e "${GREEN}All required dependencies are installed!${NC}"
echo ""

# Warning
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  • This will load eBPF programs into the kernel"
echo "  • Some reduction strategies may pause/slow processes"
echo "  • You can safely exit with Ctrl+C at any time"
echo ""

read -p "Press ENTER to start eBPF monitoring, or Ctrl+C to exit... "

echo ""
echo -e "${MAGENTA}🔥 Loading eBPF programs...${NC}"
echo ""

# Run the eBPF interactive program
python3 pycode/main_ebpf_interactive.py

# Exit message
echo ""
echo -e "${GREEN}Thank you for using eBPF Carbon Emission Monitor!${NC}"
echo -e "${BLUE}eBPF: Low overhead, high accuracy! 🚀${NC}"
echo ""
