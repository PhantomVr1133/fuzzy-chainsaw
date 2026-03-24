#!/usr/bin/env python3
"""
RepairOS — 1.54" LCD Screen UI (240x240)
ST7789 SPI Display for Raspberry Pi Zero 2 W

Wiring (physical pins):
  VCC  → Pin 17 (3.3V)
  GND  → Pin 20 (GND)
  DIN  → Pin 19 (SPI0 MOSI / GPIO10)
  CLK  → Pin 23 (SPI0 SCLK / GPIO11)
  CS   → Pin 24 (SPI0 CE0  / GPIO8)
  DC   → Pin 18 (GPIO24)
  RST  → Pin 22 (GPIO25)
  BL   → Pin 12 (GPIO18) — backlight
"""

import st7789
import psutil
import json
import os
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont

# ─── Display Setup ────────────────────────────────────────────
disp = st7789.ST7789(
    height=240,
    width=240,
    rotation=90,
    port=0,
    cs=0,
    dc=24,
    rst=25,
    backlight=18,
    spi_speed_hz=80 * 1000 * 1000
)

W, H = 240, 240

# ─── Fonts ────────────────────────────────────────────────────
FONT_PATH = "/usr/share/fonts/truetype/dejavu/"
try:
    font_tiny  = ImageFont.truetype(FONT_PATH + "DejaVuSansMono.ttf", 9)
    font_sm    = ImageFont.truetype(FONT_PATH + "DejaVuSansMono.ttf", 11)
    font_md    = ImageFont.truetype(FONT_PATH + "DejaVuSansMono.ttf", 14)
    font_lg    = ImageFont.truetype(FONT_PATH + "DejaVuSansMono.ttf", 20)
    font_xl    = ImageFont.truetype(FONT_PATH + "DejaVuSansMono.ttf", 30)
    font_bold  = ImageFont.truetype(FONT_PATH + "DejaVuSansMono-Bold.ttf", 12)
    font_bold_sm = ImageFont.truetype(FONT_PATH + "DejaVuSansMono-Bold.ttf", 10)
except:
    font_tiny = font_sm = font_md = font_lg = font_xl = font_bold = font_bold_sm = ImageFont.load_default()

# ─── Colors ───────────────────────────────────────────────────
BG       = (6,   6,  16)
GREEN    = (57, 255, 106)
DIM      = (40,  60,  40)
WHITE    = (220, 220, 230)
RED      = (255,  68,  85)
YELLOW   = (255, 204,  68)
BLUE     = ( 68, 170, 255)
PURPLE   = (170, 136, 255)
TEAL     = ( 29, 158, 117)
ORANGE   = (186, 117,  23)
DARKBG   = (10,  10,  26)
PANELBG  = (12,  12,  24)

# ─── XP System ───────────────────────────────────────────────
BASE = "/home/pi/repairos"
XP_FILE = f"{BASE}/xp.json"

LEVELS = [
    "Newbie Fixer","Cable Wrangler","Boot Whisperer","Kernel Knight",
    "RAM Ranger","Disk Defender","System Sage","Pi Master",
    "OS Oracle","RepairOS Legend"
]
PETS = [
    {"name":"BITSY",  "icon":"(*)",  "min_level":1},
    {"name":"BYTE",   "icon":"(o)",  "min_level":3},
    {"name":"CHIRP",  "icon":"(-)", "min_level":5},
    {"name":"PIXEL",  "icon":"(^)", "min_level":7},
    {"name":"NEXUS",  "icon":"(@)", "min_level":9},
    {"name":"DRACO",  "icon":"(D)", "min_level":10},
]

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE) as f:
            return json.load(f)
    return {"xp":0,"level":1,"fixes":0,"pet_hp":30}

def save_xp(d):
    with open(XP_FILE,"w") as f:
        json.dump(d,f)

def award_xp(amount, num_fixes=1):
    d = load_xp()
    d["xp"] += amount
    d["fixes"] += num_fixes
    d["pet_hp"] = min(100, d.get("pet_hp",30) + 15)
    d["level"] = d["xp"]//200 + 1
    save_xp(d)
    return d

def get_pet(level):
    pet = PETS[0]
    for p in PETS:
        if level >= p["min_level"]:
            pet = p
    return pet

# ─── Draw Helpers ─────────────────────────────────────────────
def bar(draw, x, y, w, h, pct, color, bg=DARKBG):
    draw.rectangle([x, y, x+w, y+h], fill=bg)
    fw = int(w * min(pct,100) / 100)
    if fw > 0:
        draw.rectangle([x, y, x+fw, y+h], fill=color)

def topbar(draw, title, right=""):
    draw.rectangle([0, 0, 240, 18], fill=PANELBG)
    draw.line([0, 18, 240, 18], fill=(20,40,20), width=1)
    draw.text((6, 3), title, font=font_bold, fill=GREEN)
    if right:
        draw.text((180, 3), right, font=font_tiny, fill=DIM)

# ─── Screen Pages ─────────────────────────────────────────────
PAGE_HOME  = 0
PAGE_SCAN  = 1
PAGE_XP    = 2

def draw_home(stats, xp_data):
    img = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(img)
    pet = get_pet(xp_data["level"])
    topbar(d, "REPAIROS v1.0",
           time.strftime("%H:%M"))

    # Pet row
    d.rectangle([0, 19, 239, 68], fill=PANELBG)
    d.text((8, 22), pet["icon"], font=font_lg, fill=PURPLE)
    d.text((50, 22), pet["name"], font=font_bold, fill=PURPLE)
    d.text((50, 35), f"lv.{xp_data['level']}  {xp_data['xp']}XP", font=font_tiny, fill=DIM)
    hp = xp_data.get("pet_hp", 30)
    d.text((50, 46), f"HP:", font=font_tiny, fill=DIM)
    bar(d, 68, 48, 100, 5, hp, TEAL)
    d.text((172, 46), f"{hp}%", font=font_tiny, fill=TEAL)
    d.line([0,68,239,68], fill=(15,25,15), width=1)

    # Stats grid
    panels = [
        ("CPU",  f"{stats['cpu']:.0f}%",  stats["cpu"],  BLUE,   8,  74),
        ("RAM",  f"{stats['ram']:.0f}%",  stats["ram"],  TEAL,  124,  74),
        ("DISK", f"{stats['disk']:.0f}%", stats["disk"], ORANGE, 8, 130),
        ("TEMP", f"{stats['temp']:.0f}C", min(stats["temp"],100), RED, 124, 130),
    ]
    for label, val, pct, color, px, py in panels:
        d.rectangle([px, py, px+108, py+50], fill=PANELBG)
        d.rectangle([px, py, px+108, py+50], outline=(20,30,20), width=1)
        d.text((px+6, py+5), label, font=font_tiny, fill=DIM)
        d.text((px+6, py+17), val, font=font_lg, fill=color)
        bar(d, px+6, py+43, 96, 4, pct, color)

    # Menu
    d.rectangle([0, 186, 239, 239], fill=PANELBG)
    d.line([0,186,239,186], fill=(15,25,15), width=1)
    d.text((8,  192), "[A]", font=font_bold, fill=GREEN)
    d.text((36, 192), "Run scan", font=font_sm, fill=WHITE)
    d.text((150,192), "+XP", font=font_tiny, fill=PURPLE)
    d.text((8,  212), "[B]", font=font_bold, fill=PURPLE)
    d.text((36, 212), "XP + Pet", font=font_sm, fill=WHITE)
    d.text((150,212), f"{xp_data['fixes']} fixes", font=font_tiny, fill=DIM)
    return img

def draw_scan(issues, status="SCANNING...", done=False):
    img = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(img)
    topbar(d, status, "← [B]")
    y = 24
    for iss in issues[:5]:
        sev_c = {"critical":RED,"high":YELLOW,"medium":BLUE}.get(iss["severity"],DIM)
        d.rectangle([0, y, 239, y+36], fill=PANELBG)
        d.line([0, y+36, 239, y+36], fill=(15,15,30), width=1)
        d.ellipse([8, y+14, 16, y+22], fill=sev_c)
        d.text((22, y+4), iss["name"][:22], font=font_bold_sm, fill=WHITE)
        d.text((22, y+17), iss["detail"], font=font_tiny, fill=DIM)
        d.text((22, y+27), iss["severity"].upper(), font=font_tiny, fill=sev_c)
        d.text((180,y+27), f"+{iss['xp']}XP", font=font_tiny, fill=PURPLE)
        y += 38

    if not issues and done:
        d.text((30, 100), "No issues!", font=font_md, fill=GREEN)
        d.text((20, 122), "System is healthy", font=font_sm, fill=DIM)

    if done and issues:
        d.rectangle([0, 200, 239, 239], fill=PANELBG)
        d.line([0,200,239,200], fill=(15,15,30), width=1)
        d.text((20, 208), "[A] FIX ALL", font=font_bold, fill=GREEN)
        d.text((140,208), "[B] SKIP", font=font_bold, fill=DIM)
    return img

def draw_xp(xp_data):
    img = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(img)
    topbar(d, "XP + PET", "← [B]")

    lvl = xp_data["level"]
    xp = xp_data["xp"]
    in_lv = xp % 200
    pet = get_pet(lvl)
    title = LEVELS[min(lvl-1, len(LEVELS)-1)]
    hp = xp_data.get("pet_hp",30)

    # XP big number
    d.text((W//2 - 40, 26), f"{xp}", font=font_xl, fill=GREEN)
    d.text((W//2 - 12, 60), "XP", font=font_sm, fill=DIM)
    bar(d, 10, 78, 220, 7, (in_lv / 200) * 100, PURPLE)
    d.text((10, 88), f"LV {lvl} — {title}", font=font_tiny, fill=PURPLE)
    d.text((170,88), f"{200-in_lv} left", font=font_tiny, fill=DIM)

    # Pet
    d.line([0,100,239,100], fill=(20,20,40), width=1)
    d.text((100, 108), pet["icon"], font=font_xl, fill=PURPLE)
    d.text((90, 145), pet["name"], font=font_bold, fill=PURPLE)
    mood = "happy & healthy!" if hp >= 60 else "needs more fixes..."
    d.text((60, 160), mood, font=font_tiny, fill=DIM)
    d.text((8, 172), "HP:", font=font_tiny, fill=DIM)
    bar(d, 30, 173, 170, 5, hp, TEAL)
    d.text((205,170), f"{hp}%", font=font_tiny, fill=TEAL)

    # Evolution chain
    d.line([0,185,239,185], fill=(20,20,40), width=1)
    d.text((6, 188), "EVOLUTIONS:", font=font_tiny, fill=DIM)
    stages = ["(*)", "(o)", "(-)", "(^)", "(@)", "(D)"]
    mins   = [1, 3, 5, 7, 9, 10]
    for i, (icon, ml) in enumerate(zip(stages, mins)):
        px = 6 + i * 38
        col = GREEN if lvl >= ml else DIM
        d.text((px, 200), icon, font=font_tiny, fill=col)
        d.text((px, 212), f"L{ml}", font=font_tiny, fill=DIM)

    # Fixes
    d.rectangle([0,226,239,239], fill=PANELBG)
    d.text((8, 229), f"Total fixes: {xp_data['fixes']}", font=font_tiny, fill=DIM)
    return img

# ─── Scan Logic ───────────────────────────────────────────────
def get_system_stats():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    temp = 0
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read()) / 1000
    except:
        pass
    return {"cpu":cpu,"ram":ram,"disk":disk,"temp":temp}

def scan_for_issues():
    stats = get_system_stats()
    issues = []
    if stats["disk"] > 80:
        issues.append({"name":"Low disk space","detail":f'{stats["disk"]:.0f}% used',"severity":"high","xp":50})
    if stats["ram"] > 80:
        issues.append({"name":"High RAM usage","detail":f'{stats["ram"]:.0f}% used',"severity":"high","xp":30})
    if stats["temp"] > 70:
        issues.append({"name":"High CPU temp","detail":f'{stats["temp"]:.1f}C',"severity":"critical","xp":100})
    try:
        result = subprocess.run(["apt","list","--upgradable"], capture_output=True, text=True, timeout=8)
        c = result.stdout.count("upgradable")
        if c > 5:
            issues.append({"name":"Outdated packages","detail":f"{c} updates","severity":"medium","xp":40})
    except:
        pass
    return issues, stats

def fix_all_issues(issues):
    for iss in issues:
        if "disk" in iss["name"].lower():
            subprocess.run(["apt","clean"], capture_output=True)
        elif "ram" in iss["name"].lower():
            subprocess.run(["sync"])
            try:
                with open("/proc/sys/vm/drop_caches","w") as f: f.write("3\n")
            except: pass
        elif "temp" in iss["name"].lower():
            subprocess.run(["cpufreq-set","-g","powersave"], capture_output=True)
        elif "package" in iss["name"].lower():
            subprocess.run(["apt","upgrade","-y"], capture_output=True, timeout=60)

# ─── Button Setup ─────────────────────────────────────────────
BTN_A = 5   # change to match your board's button pins
BTN_B = 6
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    BUTTONS_OK = True
except:
    BUTTONS_OK = False

def btn_pressed(pin):
    if not BUTTONS_OK:
        return False
    import RPi.GPIO as GPIO
    return GPIO.input(pin) == GPIO.LOW

# ─── Main Loop ────────────────────────────────────────────────
def main():
    page = PAGE_HOME
    last_stats = get_system_stats()
    xp_data = load_xp()
    scan_issues = []
    scan_done = False
    last_refresh = 0

    print("RepairOS screen running. Press Ctrl+C to stop.")
    print("Buttons: A=GPIO5  B=GPIO6  (edit script to change)")

    while True:
        now = time.time()

        # Refresh stats every 5s on home
        if page == PAGE_HOME and now - last_refresh > 5:
            last_stats = get_system_stats()
            xp_data = load_xp()
            last_refresh = now
            img = draw_home(last_stats, xp_data)
            disp.display(img)

        # Button A
        if btn_pressed(BTN_A):
            time.sleep(0.05)
            if not btn_pressed(BTN_A):
                continue
            if page == PAGE_HOME:
                page = PAGE_SCAN
                scan_done = False
                img = draw_scan([], "SCANNING...", False)
                disp.display(img)
                time.sleep(0.1)
                scan_issues, last_stats = scan_for_issues()
                scan_done = True
                title = f"{len(scan_issues)} ISSUES" if scan_issues else "ALL CLEAR!"
                img = draw_scan(scan_issues, title, True)
                disp.display(img)
            elif page == PAGE_SCAN and scan_done and scan_issues:
                img = draw_scan(scan_issues, "FIXING...", False)
                disp.display(img)
                fix_all_issues(scan_issues)
                total_xp = sum(i["xp"] for i in scan_issues)
                xp_data = award_xp(total_xp, num_fixes=len(scan_issues))
                scan_issues = []
                img = draw_scan([], "ALL FIXED!", True)
                disp.display(img)
                time.sleep(1.5)
                page = PAGE_HOME
                last_stats = get_system_stats()
                img = draw_home(last_stats, xp_data)
                disp.display(img)
            time.sleep(0.3)

        # Button B — go back / go to XP page
        if btn_pressed(BTN_B):
            time.sleep(0.05)
            if not btn_pressed(BTN_B):
                continue
            if page == PAGE_HOME:
                page = PAGE_XP
                xp_data = load_xp()
                img = draw_xp(xp_data)
                disp.display(img)
            elif page in (PAGE_SCAN, PAGE_XP):
                page = PAGE_HOME
                last_stats = get_system_stats()
                xp_data = load_xp()
                img = draw_home(last_stats, xp_data)
                disp.display(img)
            time.sleep(0.3)

        time.sleep(0.05)

if __name__ == "__main__":
    # Initial draw
    stats = get_system_stats()
    xp = load_xp()
    disp.display(draw_home(stats, xp))
    main()
