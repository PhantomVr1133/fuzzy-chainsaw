#!/usr/bin/env python3
"""
RepairOS — Terminal Repair Tool
Scans, fixes, awards XP, and manages your pet
"""

import psutil, platform, json, os, subprocess, socket, time

BASE    = "/home/pi/repairos"
XP_FILE = f"{BASE}/xp.json"
LOG_FILE= f"{BASE}/repair.log"

LEVELS = [
    "Newbie Fixer","Cable Wrangler","Boot Whisperer","Kernel Knight",
    "RAM Ranger","Disk Defender","System Sage","Pi Master",
    "OS Oracle","RepairOS Legend"
]
PETS = [
    {"name":"Bitsy", "emoji":"🐣","min_level":1},
    {"name":"Byte",  "emoji":"🐥","min_level":3},
    {"name":"Chirp", "emoji":"🐦","min_level":5},
    {"name":"Pixel", "emoji":"🦅","min_level":7},
    {"name":"Nexus", "emoji":"🦉","min_level":9},
    {"name":"Draco", "emoji":"🐉","min_level":10},
]

# ─── XP ────────────────────────────────────────────────────────

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE) as f:
            return json.load(f)
    return {"xp":0,"level":1,"fixes":0,"pet_hp":30}

def save_xp(data):
    with open(XP_FILE,"w") as f:
        json.dump(data, f, indent=2)

def get_pet(level):
    pet = PETS[0]
    for p in PETS:
        if level >= p["min_level"]:
            pet = p
    return pet

def award_xp(amount, num_fixes=1):
    data = load_xp()
    old_level = data["level"]
    data["xp"]    += amount
    data["fixes"] += num_fixes
    data["pet_hp"] = min(100, data.get("pet_hp", 30) + 15)
    data["level"]  = data["xp"] // 200 + 1
    save_xp(data)
    log_action(f"+{amount} XP — {num_fixes} fix(es)")
    print(f"\n  ⭐  +{amount} XP  |  Total: {data['xp']} XP  |  Level {data['level']}")
    pet = get_pet(data["level"])
    print(f"  🐾  {pet['emoji']} {pet['name']} — happiness {data['pet_hp']}%")
    if data["level"] > old_level:
        title = LEVELS[min(data["level"]-1, len(LEVELS)-1)]
        print(f"\n  🎉  LEVEL UP! You are now Level {data['level']}: {title}!")
        print(f"  🐾  Pet evolved to {get_pet(data['level'])['name']}!")
    return data

def log_action(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(BASE, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

# ─── Detection ─────────────────────────────────────────────────

def detect_system():
    info = {
        "os":       platform.system(),
        "release":  platform.release(),
        "machine":  platform.machine(),
        "hostname": socket.gethostname(),
        "ip":       "unknown",
        "is_pi":    False,
        "pi_model": "unknown",
        "is_server":False,
    }
    try:
        info["ip"] = socket.gethostbyname(socket.gethostname())
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        if "Raspberry Pi" in cpuinfo:
            info["is_pi"] = True
            for line in cpuinfo.splitlines():
                if "Model" in line:
                    info["pi_model"] = line.split(":")[1].strip()
        if "Zero 2" in cpuinfo:
            info["pi_model"] = "Raspberry Pi Zero 2 W"
    except Exception:
        pass
    if any(h in (info["version"] if "version" in info else "").lower()
           for h in ["server","ubuntu","debian","centos","rhel","fedora"]):
        info["is_server"] = True
    return info

# ─── Scanner ───────────────────────────────────────────────────

def scan_problems():
    issues = []

    try:
        disk = psutil.disk_usage("/")
        if disk.percent > 85:
            issues.append({"id":"low_disk","name":"Low disk space",
                "detail":f"{disk.percent:.1f}% used","severity":"high","xp":50})
    except Exception:
        pass

    try:
        ram = psutil.virtual_memory()
        if ram.percent > 85:
            issues.append({"id":"high_ram","name":"High RAM usage",
                "detail":f"{ram.percent:.1f}% used","severity":"medium","xp":30})
    except Exception:
        pass

    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read()) / 1000
        if temp > 75:
            issues.append({"id":"high_temp","name":"High CPU temperature",
                "detail":f"{temp:.1f}°C","severity":"critical","xp":100})
    except Exception:
        pass

    try:
        zombies = [p for p in psutil.process_iter(["status"])
                   if p.info["status"] == psutil.STATUS_ZOMBIE]
        if zombies:
            issues.append({"id":"zombies","name":"Zombie processes",
                "detail":f"{len(zombies)} found","severity":"medium","xp":35})
    except Exception:
        pass

    try:
        swap = psutil.swap_memory()
        if swap.total > 0 and swap.percent > 80:
            issues.append({"id":"high_swap","name":"Swap overloaded",
                "detail":f"{swap.percent:.1f}% used","severity":"high","xp":45})
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["apt","list","--upgradable"],
            capture_output=True, text=True, timeout=10
        )
        count = result.stdout.count("upgradable")
        if count > 5:
            issues.append({"id":"outdated_pkgs","name":"Outdated packages",
                "detail":f"{count} updates available","severity":"medium","xp":40})
    except Exception:
        pass

    return issues

# ─── Fixes ─────────────────────────────────────────────────────

def fix_issue(issue):
    iid = issue["id"]
    if iid == "low_disk":
        subprocess.run(["apt","clean"], capture_output=True)
        subprocess.run(["journalctl","--vacuum-size=50M"], capture_output=True)
        subprocess.run(["find","/tmp","-type","f","-delete"], capture_output=True)
    elif iid == "high_ram":
        subprocess.run(["sync"])
        try:
            with open("/proc/sys/vm/drop_caches","w") as f:
                f.write("3\n")
        except Exception:
            pass
    elif iid == "high_temp":
        subprocess.run(["cpufreq-set","-g","powersave"], capture_output=True)
    elif iid == "zombies":
        subprocess.run(["kill","-s","SIGCHLD","1"], capture_output=True)
    elif iid == "high_swap":
        subprocess.run(["swapoff","-a"], capture_output=True)
        subprocess.run(["swapon","-a"], capture_output=True)
    elif iid == "outdated_pkgs":
        subprocess.run(["apt","upgrade","-y"], capture_output=True, timeout=120)

# ─── Network Scanner ───────────────────────────────────────────

def scan_network():
    print("\n  Scanning local network...")
    try:
        result = subprocess.run(
            ["nmap","-sn","192.168.1.0/24"],
            capture_output=True, text=True, timeout=30
        )
        lines = [l for l in result.stdout.splitlines() if "Nmap scan report" in l]
        print(f"  Found {len(lines)} device(s):")
        for l in lines:
            print(f"    {l.replace('Nmap scan report for ','')}")
    except Exception:
        print("  nmap not found — run: sudo apt install nmap")

# ─── Main ──────────────────────────────────────────────────────

def main():
    print("\n" + "="*46)
    print("     RepairOS  —  Pi Zero 2 W")
    print("="*46)

    info = detect_system()
    print(f"\n  OS       : {info['os']} {info['release']}")
    print(f"  Machine  : {info['machine']}")
    print(f"  Hostname : {info['hostname']}  ({info['ip']})")
    if info["is_pi"]:
        print(f"  Device   : ✓ {info['pi_model']}")
    if info["is_server"]:
        print(f"  Type     : Server OS detected")

    data  = load_xp()
    pet   = get_pet(data["level"])
    title = LEVELS[min(data["level"]-1, len(LEVELS)-1)]
    print(f"\n  Player   : Level {data['level']} — {title}")
    print(f"  XP       : {data['xp']} total  |  {200 - data['xp']%200} to next level")
    print(f"  Pet      : {pet['emoji']} {pet['name']} — happiness {data.get('pet_hp',30)}%")
    print(f"  Fixes    : {data['fixes']} total")

    print("\n  [1] Run full scan + fix")
    print("  [2] Scan network")
    print("  [3] View log")
    print("  [4] Exit")
    print("\n  Choice: ", end="")

    choice = input().strip()

    if choice == "1":
        print("\n  Scanning...")
        issues = scan_problems()
        if not issues:
            print("  ✓ No problems found!")
            award_xp(10, num_fixes=1)
        else:
            print(f"\n  Found {len(issues)} issue(s):\n")
            for i, iss in enumerate(issues):
                print(f"  [{i+1}] {iss['name']} — {iss['detail']}  [{iss['severity'].upper()}]  +{iss['xp']} XP")
            print("\n  Fix all? (y/n): ", end="")
            if input().strip().lower() == "y":
                for iss in issues:
                    print(f"\n  Fixing: {iss['name']}...")
                    fix_issue(iss)
                total_xp = sum(i["xp"] for i in issues)
                award_xp(total_xp, num_fixes=len(issues))

    elif choice == "2":
        scan_network()

    elif choice == "3":
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                lines = f.readlines()[-20:]
            print("\n  Last 20 entries:")
            for l in lines:
                print(f"  {l.rstrip()}")
        else:
            print("  No log yet.")

    print("\n  Done! Run again: python3 /home/pi/repairos/scripts/repair.py\n")

if __name__ == "__main__":
    main()
