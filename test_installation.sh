#!/bin/bash

# Test script to verify Network Monitor installation
# Run with: sudo bash test_installation.sh

echo "======================================================================"
echo "Network Monitor - Installation Test"
echo "======================================================================"
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "Running installation tests..."
echo

# Test 1: Check if running as root
run_test "Root privileges" "[ \$EUID -eq 0 ]"

# Test 2: Check Python 3
run_test "Python 3 installed" "python3 --version"

# Test 3: Check pip3
run_test "pip3 installed" "pip3 --version"

# Test 4: Check scapy
run_test "scapy module" "python3 -c 'import scapy'"

# Test 5: Check psutil
run_test "psutil module" "python3 -c 'import psutil'"

# Test 6: Check netifaces
run_test "netifaces module" "python3 -c 'import netifaces'"

# Test 7: Check tkinter
run_test "tkinter module" "python3 -c 'import tkinter'"

# Test 8: Check if main.py exists
run_test "main.py exists" "[ -f main.py ]"

# Test 9: Check if main.py is executable
run_test "main.py executable" "[ -x main.py ]"

# Test 10: Check project files
run_test "gui.py exists" "[ -f gui.py ]"
run_test "packet_capture.py exists" "[ -f packet_capture.py ]"
run_test "process_mapper.py exists" "[ -f process_mapper.py ]"
run_test "database_logger.py exists" "[ -f database_logger.py ]"
run_test "config.py exists" "[ -f config.py ]"

# Test 11: Syntax check
echo -n "Testing: Python syntax... "
if python3 -m py_compile main.py gui.py packet_capture.py process_mapper.py database_logger.py config.py 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 12: Import check
echo -n "Testing: Module imports... "
if python3 -c "from packet_capture import PacketCapture; from database_logger import DatabaseLogger; from process_mapper import ProcessMapper" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo
echo "======================================================================"
echo "Test Results"
echo "======================================================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Installation is successful.${NC}"
    echo
    echo "You can now run the application with:"
    echo "  sudo python3 main.py"
    echo
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the errors above.${NC}"
    echo
    echo "Common fixes:"
    echo "  1. Install missing dependencies: sudo bash install.sh"
    echo "  2. Make sure you're running as root: sudo bash test_installation.sh"
    echo "  3. Check Python version: python3 --version (needs 3.7+)"
    echo
    exit 1
fi
