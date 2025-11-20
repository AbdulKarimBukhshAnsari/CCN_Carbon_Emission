#!/bin/bash

# Carbon Emission Monitor Runner Script
# This script must be run with sudo privileges

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Carbon Emission Monitor using eBPF${NC}"
echo "========================================"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run with sudo${NC}"
    echo "Usage: sudo ./run.sh"
    exit 1
fi

# Check if BCC is installed
if ! dpkg -l | grep -q python3-bpfcc; then
    echo -e "${RED}Error: python3-bpfcc is not installed${NC}"
    echo "Install it with: sudo apt-get install python3-bpfcc bpfcc-tools"
    exit 1
fi

echo -e "${GREEN}✓ Running with sudo privileges${NC}"
echo -e "${GREEN}✓ BCC tools detected${NC}"
echo ""

# Run the Python script
python3 pycode/main.py
