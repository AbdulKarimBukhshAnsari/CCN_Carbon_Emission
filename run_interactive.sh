#!/bin/bash

# Interactive Carbon Emission Monitor Runner Script
# For CEP (Carbon Emission Project) Demonstration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     🌍 CARBON EMISSION MONITOR & REDUCTION SYSTEM 🌍          ║"
echo "║                                                                ║"
echo "║          Interactive CEP Demonstration Tool                    ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}This tool will:${NC}"
echo "  1. Monitor your system's carbon emissions"
echo "  2. Identify top carbon-emitting processes"
echo "  3. Apply REAL reduction strategies"
echo "  4. Show you the actual carbon savings"
echo ""

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check psutil
if python3 -c "import psutil" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-psutil installed"
else
    echo -e "${RED}✗${NC} python3-psutil not found"
    echo "  Install with: sudo apt-get install python3-psutil"
    exit 1
fi

# Check prettytable
if python3 -c "import prettytable" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-prettytable installed"
else
    echo -e "${RED}✗${NC} python3-prettytable not found"
    echo "  Install with: sudo apt-get install python3-prettytable"
    exit 1
fi

# Check cpulimit (optional)
if command -v cpulimit &> /dev/null; then
    echo -e "${GREEN}✓${NC} cpulimit installed (optional)"
else
    echo -e "${YELLOW}!${NC} cpulimit not found (optional, for CPU limiting)"
    echo "  Install with: sudo apt-get install cpulimit"
fi

# Check matplotlib (optional)
if python3 -c "import matplotlib" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} python3-matplotlib installed (optional)"
else
    echo -e "${YELLOW}!${NC} python3-matplotlib not found (optional, for charts)"
    echo "  Install with: sudo apt-get install python3-matplotlib"
fi

echo ""
echo -e "${GREEN}All required dependencies are installed!${NC}"
echo ""

# Ask for confirmation
echo -e "${YELLOW}Ready to start?${NC}"
echo "  • This will monitor your system"
echo "  • You'll choose a reduction strategy"
echo "  • Some strategies may pause/slow processes temporarily"
echo ""
read -p "Press ENTER to continue, or Ctrl+C to exit... "

echo ""
echo -e "${BLUE}Starting Carbon Emission Monitor...${NC}"
echo ""

# Run the interactive program
python3 pycode/main_interactive.py

# Exit message
echo ""
echo -e "${GREEN}Thank you for using Carbon Emission Monitor!${NC}"
echo -e "${BLUE}Every joule saved makes a difference! 🌱${NC}"
echo ""
