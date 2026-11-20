#!/usr/bin/env bash
# language: Bash, file: run.sh, runtime: Termux / Linux / macOS
# X-TREX one-shot launcher — download latest + run.
set -e

# ─── konfigurasi ────────────────────────────────────
# GANTI dengan user/repo GitHub js setelah push
GH_USER="skyyror"
GH_REPO="xtrex"
GH_BRANCH="main"
RAW="https://raw.githubusercontent.com/${GH_USER}/${GH_REPO}/${GH_BRANCH}"

INSTALL_DIR="$HOME/.xtrex"
XTREX_PY="$INSTALL_DIR/xtrex.py"

# ─── deteksi Python ─────────────────────────────────
if [ -d "/data/data/com.termux" ]; then
    if ! command -v python >/dev/null 2>&1; then
        echo "[*] python belum ada, install dulu…"
        pkg install python -y
    fi
    PY="python"
else
    if command -v python3 >/dev/null 2>&1; then
        PY="python3"
    elif command -v python >/dev/null 2>&1; then
        PY="python"
    else
        echo "[!] python tidak ditemukan. install dulu."
        exit 1
    fi
fi

# ─── pastikan curl/wget ada ─────────────────────────
if command -v curl >/dev/null 2>&1; then
    DL="curl -sL"
elif command -v wget >/dev/null 2>&1; then
    DL="wget -qO-"
else
    if [ -d "/data/data/com.termux" ]; then
        echo "[*] curl belum ada, install dulu…"
        pkg install curl -y
        DL="curl -sL"
    else
        echo "[!] curl / wget tidak ditemukan."
        exit 1
    fi
fi

# ─── download xtrex.py ──────────────────────────────
mkdir -p "$INSTALL_DIR"
echo "[*] download xtrex.py terbaru dari GitHub…"
$DL "${RAW}/xtrex.py" -o "$XTREX_PY" 2>/dev/null || \
    $DL "${RAW}/xtrex.py" > "$XTREX_PY"

# sanity check — file harus > 10 KB dan ada string X-TREX
SIZE=$(wc -c < "$XTREX_PY" 2>/dev/null || echo 0)
if [ "$SIZE" -lt 10000 ] || ! grep -q "X-TREX" "$XTREX_PY" 2>/dev/null; then
    echo "[!] download gagal / file rusak (ukuran $SIZE byte)."
    echo "    cek URL: ${RAW}/xtrex.py"
    rm -f "$XTREX_PY"
    exit 1
fi

chmod +x "$XTREX_PY"
echo "[*] ok ($SIZE byte) — jalankan."
cd "$INSTALL_DIR"
exec "$PY" "$XTREX_PY"
