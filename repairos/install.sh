#!/bin/bash
# ============================================
#   RepairOS — One-Line GitHub Installer
#   Usage: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/repairos/main/install.sh | sudo bash
# ============================================

set -e

REPO="https://raw.githubusercontent.com/YOUR_USERNAME/repairos/main"
INSTALL_DIR="/home/pi/repairos"
SCRIPTS_DIR="$INSTALL_DIR/scripts"

echo ""
echo "========================================"
echo "   RepairOS Installer — Pi Zero 2 W"
echo "========================================"
echo ""

# ── 1. Create directories ──────────────────
echo "[1/6] Creating directories..."
mkdir -p "$SCRIPTS_DIR"

# ── 2. Enable SPI ─────────────────────────
echo "[2/6] Enabling SPI..."
raspi-config nonint do_spi 0

# ── 3. Install system packages ────────────
echo "[3/6] Installing system packages..."
apt-get update -qq
apt-get install -y python3-pip python3-spidev python3-rpi.gpio \
    fonts-dejavu-core curl git

# ── 4. Install Python packages ────────────
echo "[4/6] Installing Python packages..."
pip3 install psutil st7789 pillow flask --break-system-packages 2>/dev/null \
    || pip3 install psutil st7789 pillow flask

# ── 5. Download scripts from GitHub ───────
echo "[5/6] Downloading RepairOS scripts..."
curl -sSL "$REPO/scripts/repair.py"    -o "$SCRIPTS_DIR/repair.py"
curl -sSL "$REPO/scripts/screen_ui.py" -o "$SCRIPTS_DIR/screen_ui.py"
curl -sSL "$REPO/scripts/dashboard.py" -o "$SCRIPTS_DIR/dashboard.py"

chmod +x "$SCRIPTS_DIR/"*.py
chown -R pi:pi "$INSTALL_DIR"

# ── 6. Install systemd services ───────────
echo "[6/6] Setting up auto-start services..."

cat > /etc/systemd/system/repairos-screen.service << 'SVCEOF'
[Unit]
Description=RepairOS LCD Screen UI
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/repairos/scripts/screen_ui.py
WorkingDirectory=/home/pi/repairos/scripts
User=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

cat > /etc/systemd/system/repairos-dashboard.service << 'SVCEOF'
[Unit]
Description=RepairOS Web Dashboard
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/repairos/scripts/dashboard.py
WorkingDirectory=/home/pi/repairos/scripts
User=pi
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable repairos-screen repairos-dashboard
systemctl start repairos-dashboard

echo ""
echo "========================================"
echo "   RepairOS installed!"
echo ""
PI_IP=$(hostname -I | awk '{print $1}')
echo "   Web dashboard : http://$PI_IP:5000"
echo "   Terminal tool : python3 $SCRIPTS_DIR/repair.py"
echo "   Screen starts : automatically on next boot"
echo ""
echo "   To start screen now:"
echo "   sudo systemctl start repairos-screen"
echo "========================================"
echo ""
