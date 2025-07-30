#!/bin/bash

# Function to check if a command exists
check_tool() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "[✔] $1 is installed."
    else
        echo "[✘] $1 is NOT installed!"
    fi
}

echo "[*] Verifying required tools..."

check_tool nikto
check_tool nmap
check_tool masscan
check_tool python3  # Required for unicorn.py
check_tool hping3

# Check if unicorn is present
if [ -f "/opt/unicorn/unicorn.py" ]; then
    echo "[✔] unicorn.py found in /opt/unicorn/"
else
    echo "[✘] unicorn.py not found!"
fi

echo "[✓] Tool verification completed."
