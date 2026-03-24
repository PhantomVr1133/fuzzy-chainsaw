#!/usr/bin/env python3
"""
RepairOS Web Dashboard
Visit http://<pi-ip>:5000 from any browser on your network
"""
from flask import Flask, jsonify, render_template_string
import psutil, json, os, sys

app  = Flask(__name__)
BASE = "/home/pi/repairos"
XP_FILE = f"{BASE}/xp.json"

sys.path.insert(0, f"{BASE}/scripts")

HTML = """<!DOCTYPE html>
<html>
<head>
<title>RepairOS Dashboard</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#060610;color:#dde;font-family:monospace;padding:16px}
  h1{color:#39ff6a;font-size:1.3rem;margin-bottom:16px}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:16px}
  .card{background:#0d0d1f;border:1px solid #1a1a3a;border-radius:8px;padding:12px}
  .lbl{font-size:10px;color:#4a5a4a;margin-bottom:4px}
  .val{font-size:24px;font-weight:bold;color:#39ff6a}
  .bar{height:5px;background:#111;border-radius:3px;margin-top:6px}
  .fill{height:100%;border-radius:3px;transition:width 1s}
  .issue{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#0d0d1f;border:1px solid #1a1a3a;border-radius:8px;margin-bottom:6px}
  .fix{background:#0a1a0a;color:#39ff6a;border:1px solid #1a3a1a;padding:4px 10px;border-radius:6px;cursor:pointer;font-family:monospace;font-size:12px}
  .fix:hover{background:#142814}
  .pet{background:#0d0d1f;border:1px solid #1a1a3a;border-radius:8px;padding:12px;margin-bottom:16px;display:flex;align-items:center;gap:12px}
  .xpb{height:6px;background:#111;border-radius:3px;margin:6px 0}
  .xpf{height:100%;border-radius:3px;background:#7f77dd;transition:width 1s}
  .scan{width:100%;padding:9px;background:#0a1a0a;color:#39ff6a;border:1px solid #1a3a1a;border-radius:8px;font-family:monospace;font-size:13px;cursor:pointer;margin-bottom:12px}
  .scan:hover{background:#142814}
  .log{background:#04040c;border:1px solid #111;border-radius:8px;padding:10px;font-size:10px;max-height:110px;overflow-y:auto}
  .ok{color:#39ff6a}.warn{color:#ffcc44}.xpc{color:#aa88ff}
</style>
</head>
<body>
<h1>🍓 RepairOS Dashboard</h1>
<div id="root">Loading...</div>
<script>
const LEVELS=["Newbie Fixer","Cable Wrangler","Boot Whisperer","Kernel Knight","RAM Ranger","Disk Defender","System Sage","Pi Master","OS Oracle","RepairOS Legend"];
const PETS=[["🐣","Bitsy"],["🐥","Byte"],["🐦","Chirp"],["🦅","Pixel"],["🦉","Nexus"],["🐉","Draco"]];
let xp=0,level=1,fixes=0,petHp=30,issues=[],logs=[];

function addLog(m,c='ok'){const t=new Date().toLocaleTimeString('en',{hour12:false});logs.unshift('<span class="'+c+'">['+t+'] '+m+'</span>');if(logs.length>30)logs.pop();}

function render(s){
  const stage=Math.min(Math.floor((level-1)/2),5);
  const inLv=xp%200;
  document.getElementById('root').innerHTML=`
  <div class="pet">
    <span style="font-size:38px">${PETS[stage][0]}</span>
    <div style="flex:1">
      <div style="font-size:14px;font-weight:bold;color:#aa88ff">${PETS[stage][1]}</div>
      <div style="font-size:11px;color:#4a5a4a">${petHp>=60?'happy & healthy!':'needs more fixes...'}</div>
      <div class="bar"><div class="fill" style="width:${petHp}%;background:#1D9E75"></div></div>
    </div>
    <div style="text-align:right"><div class="lbl">happiness</div><div style="font-size:18px;font-weight:bold;color:#1D9E75">${petHp}%</div></div>
  </div>
  <div class="grid">
    <div class="card"><div class="lbl">level</div><div class="val">${level}</div><div style="font-size:10px;color:#4a5a4a;margin-top:4px">${LEVELS[Math.min(level-1,9)]}</div></div>
    <div class="card"><div class="lbl">total xp</div><div class="val">${xp}</div><div class="xpb"><div class="xpf" style="width:${(inLv/200*100).toFixed(0)}%"></div></div><div style="font-size:10px;color:#4a5a4a">${200-inLv} to next</div></div>
    <div class="card"><div class="lbl">fixes done</div><div class="val">${fixes}</div></div>
    <div class="card"><div class="lbl">cpu</div><div class="val">${s.cpu}%</div><div class="bar"><div class="fill" style="width:${s.cpu}%;background:#378ADD"></div></div></div>
    <div class="card"><div class="lbl">ram</div><div class="val">${s.ram}%</div><div class="bar"><div class="fill" style="width:${s.ram}%;background:#1D9E75"></div></div></div>
    <div class="card"><div class="lbl">disk</div><div class="val">${s.disk}%</div><div class="bar"><div class="fill" style="width:${s.disk}%;background:#BA7517"></div></div></div>
  </div>
  <div style="font-size:10px;color:#4a5a4a;margin-bottom:6px">ISSUES</div>
  ${issues.length===0?'<div class="issue"><span>No issues — system healthy</span><span class="ok">✓</span></div>':issues.map(i=>`<div class="issue"><span>${i.name}<br><span style="font-size:10px;color:#4a5a4a">${i.detail}</span></span><button class="fix" onclick="doFix('${i.id}','${i.name}',${i.xp})">fix +${i.xp}xp</button></div>`).join('')}
  <button class="scan" onclick="doScan()">[ RUN FULL SCAN ]</button>
  <div style="font-size:10px;color:#4a5a4a;margin-bottom:5px">LOG</div>
  <div class="log">${logs.join('<br>')}</div>`;
}

async function doScan(){
  addLog('Scanning...','warn');
  const [s,sc]=await Promise.all([fetch('/api/stats').then(r=>r.json()),fetch('/api/scan').then(r=>r.json())]);
  xp=sc.xp;level=sc.level;fixes=sc.fixes;petHp=sc.pet_hp;issues=sc.issues;
  addLog(`Scan done. ${issues.length} issue(s).`,issues.length?'warn':'ok');
  render(s);
}

async function doFix(id,name,xpAmt){
  addLog('Fixing: '+name+'...','warn');
  const r=await fetch('/api/fix/'+id,{method:'POST'}).then(r=>r.json());
  xp=r.xp;level=r.level;fixes=r.fixes;petHp=r.pet_hp;
  issues=issues.filter(i=>i.id!==id);
  addLog('+'+xpAmt+' XP — fixed: '+name,'xpc');
  const s=await fetch('/api/stats').then(r=>r.json());
  render(s);
}

async function init(){
  const [s,sc]=await Promise.all([fetch('/api/stats').then(r=>r.json()),fetch('/api/scan').then(r=>r.json())]);
  xp=sc.xp;level=sc.level;fixes=sc.fixes;petHp=sc.pet_hp;issues=sc.issues;
  addLog('RepairOS dashboard ready!','ok');
  render(s);
  setInterval(async()=>{const s=await fetch('/api/stats').then(r=>r.json());render(s);},5000);
}
init();
</script>
</body></html>"""

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE) as f:
            return json.load(f)
    return {"xp":0,"level":1,"fixes":0,"pet_hp":30}

def save_xp(d):
    with open(XP_FILE,"w") as f:
        json.dump(d,f)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/stats")
def stats():
    temp = 0
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read()) / 1000
    except Exception:
        pass
    return jsonify({
        "cpu":  round(psutil.cpu_percent(interval=1), 1),
        "ram":  round(psutil.virtual_memory().percent, 1),
        "disk": round(psutil.disk_usage("/").percent, 1),
        "temp": round(temp, 1),
    })

@app.route("/api/scan")
def scan():
    import repair
    issues = repair.scan_problems()
    d = load_xp()
    return jsonify({**d, "issues": issues})

@app.route("/api/fix/<issue_id>", methods=["POST"])
def fix(issue_id):
    import repair
    issues = repair.scan_problems()
    issue  = next((i for i in issues if i["id"] == issue_id), None)
    if issue:
        repair.fix_issue(issue)
        d = load_xp()
        d["xp"]     += issue["xp"]
        d["fixes"]  += 1
        d["pet_hp"]  = min(100, d.get("pet_hp", 30) + 15)
        d["level"]   = d["xp"] // 200 + 1
        save_xp(d)
        return jsonify(d)
    return jsonify(load_xp())

if __name__ == "__main__":
    print(f"RepairOS Dashboard → http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
