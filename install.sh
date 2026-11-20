#!/data/data/com.termux/files/usr/bin/bash
# X-TREX quick install
set -e
echo "[*] installing python…"
pkg install python -y
echo "[*] clone/place xtrex.py di folder ini"
chmod +x xtrex.py 2>/dev/null || true
echo "[*] ready: python xtrex.py"
