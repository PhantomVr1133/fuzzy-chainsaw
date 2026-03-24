# 🍓 RepairOS — Raspberry Pi Zero 2 W Edition

An AI-powered computer repair OS for the Raspberry Pi Zero 2 W with a 1.54" LCD screen, XP system, and a pet that evolves as you fix things.

---

## ✨ Features

- 🔍 **Auto-detects your OS** — Linux, Windows, Mac, servers, and Raspberry Pi
- 🛠️ **Scans and fixes** — disk space, CPU temp, RAM, zombie processes, outdated packages
- ⭐ **XP + leveling system** — earn XP every time you fix something
- 🐣 **Pet that evolves** — Bitsy the egg grows into Draco the dragon at level 10
- 📺 **1.54" LCD screen UI** — live stats, scan results, XP page on your tiny screen
- 🌐 **Web dashboard** — view everything from any phone or computer on your network

---

## 🛒 What You Need

| Item | Link |
|------|------|
| Raspberry Pi Zero 2 W | [raspberrypi.com](https://www.raspberrypi.com) |
| 1.54" ST7789 240x240 LCD | Any Mini Game Console Screen Board Module |
| MicroSD card (16GB+) | — |
| Micro USB power cable | — |

---

## ⚡ One-Line Install

SSH into your Pi and run:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/repairos/main/install.sh | sudo bash
```

> Replace `YOUR_USERNAME` with your actual GitHub username after uploading.

---

## 🔌 LCD Wiring

| Display Pin | Pi Physical Pin | GPIO |
|-------------|----------------|------|
| VCC | Pin 17 | 3.3V |
| GND | Pin 20 | GND |
| DIN | Pin 19 | GPIO 10 (MOSI) |
| CLK | Pin 23 | GPIO 11 (SCLK) |
| CS  | Pin 24 | GPIO 8 (CE0) |
| DC  | Pin 18 | GPIO 24 |
| RST | Pin 22 | GPIO 25 |
| BL  | Pin 12 | GPIO 18 |

---

## 🎮 Buttons

| Button | GPIO | Action |
|--------|------|--------|
| A | GPIO 5 | Home → Run scan / Scan page → Fix all |
| B | GPIO 6 | Home → View XP & pet / Anywhere → Go back |

---

## 📁 File Structure

```
repairos/
├── install.sh          ← one-line installer (run this first)
├── scripts/
│   ├── repair.py       ← terminal repair tool + XP engine
│   ├── screen_ui.py    ← 1.54" LCD screen driver
│   └── dashboard.py    ← web dashboard (port 5000)
└── README.md
```

---

## 🚀 Usage

**Terminal repair tool:**
```bash
python3 /home/pi/repairos/scripts/repair.py
```

**Web dashboard:**
Open `http://<your-pi-ip>:5000` in any browser.

**Screen UI** starts automatically on boot. To restart manually:
```bash
sudo systemctl restart repairos-screen
```

---

## 🐾 Pet Evolution

| Level | Pet | Name |
|-------|-----|------|
| 1 | 🐣 | Bitsy |
| 3 | 🐥 | Byte |
| 5 | 🐦 | Chirp |
| 7 | 🦅 | Pixel |
| 9 | 🦉 | Nexus |
| 10 | 🐉 | Draco |

---

## 📄 License

MIT — free to use, modify, and share.
