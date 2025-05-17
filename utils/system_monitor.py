import platform
import subprocess

import os

script_path = os.path.join("herramientas", "temperatura.ps1")

def obtener_temperatura_cpu():
    script_path = os.path.join("herramientas", "temperatura.ps1")

    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        comando = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", script_path
        ]

        resultado = subprocess.check_output(comando, stderr=subprocess.STDOUT, text=True, startupinfo=si)
        return resultado.strip()

    except subprocess.CalledProcessError as e:
        return f"Error en el script de PowerShell: {e.output}"
    except Exception as e:
        return f"Error general: {e}"




print("Temperatura CPU:", obtener_temperatura_cpu())

def run_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
        return result.strip()
    except Exception as e:
        return f"Error: {str(e)}"

from concurrent.futures import ProcessPoolExecutor, as_completed

def monitor_system():
    os_name = platform.system()
    info = {}

    commands = {}

    if os_name == "Linux":
        commands = {
            "OS": "uname -a",
            "CPU Usage": "top -bn1 | grep 'Cpu(s)'",
            "Memory Usage": "free -h",
            "Disk Usage": "df -h",
            "Uptime": "uptime -p",
            "CPU Details": "lscpu",
            "Top Processes": "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 6",
            "Network Info": "ip a",
            "Network Usage": "ifstat 1 1 || cat /proc/net/dev",
            "Battery Status": "upower -i $(upower -e | grep BAT) | grep -E 'percentage|state' || acpi -b",
            "Startup Programs": "ls -1 /etc/xdg/autostart/ ~/.config/autostart/ 2>/dev/null",
            "CPU Temp": "sensors | grep -i 'core\\|temp'",
            "Disk IO Stats": "iostat -d 1 2 | tail -n 20 || iotop -b -n1 | head -n 10 || sar -d 1 1",
            "Zombie Processes": "ps aux | awk '{ if ($8 ~ /Z/) print }'",
            "Net Usage per Process": "ss -tunap",
            "Firewall Status": "ufw status",
            "Recent Logins": "last -n 5",
            "Users Logged In": "who",
            "Open Sessions": "w",
            "Insecure Permissions": "find / -perm -o+w 2>/dev/null | head -n 10",
            "System Integrity": "aide --check || chkrootkit || rkhunter --check",
            "System Updates": "apt list --upgradable 2>/dev/null || dnf check-update",
            "Active Services": "systemctl list-units --type=service --state=running",
            "Antivirus Status": "clamscan -V || echo 'No antivirus info available'"
        }

    elif os_name == "Windows":
        commands = {
            "System Model": "wmic computersystem get model",
            "OS": "wmic os get Caption,CSDVersion /value",
            "CPU Usage": "wmic cpu get loadpercentage",
            "Memory Usage": "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value",
            "Disk Usage": "wmic logicaldisk get size,freespace,caption",
            "Uptime": 'powershell -Command "(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime"',
            "CPU Details": 'wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed',
            "Top Processes": 'powershell -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | Format-Table Name,CPU,ID"',
            "Network Usage": 'powershell -Command "Get-NetAdapterStatistics | Format-Table Name,ReceivedBytes,SentBytes"',
            "Network Info": 'powershell -Command "Get-NetIPConfiguration | Format-List"',
            "Battery Status": 'powershell -Command "Get-CimInstance -ClassName Win32_Battery | Select EstimatedChargeRemaining"',
            "Startup Programs": 'powershell -Command "Get-CimInstance -ClassName Win32_StartupCommand | Select Name,Command"',
            "Disk IO Stats": 'powershell -Command "Get-Disk | Get-StoragePerformance" || powershell -Command "Get-PhysicalDisk | Format-Table DeviceId,MediaType,SerialNumber,Size,HealthStatus"',
            "Net Usage per Process": 'powershell -Command "Get-NetTCPConnection | Select-Object -First 10"',
            "Firewall Status": 'powershell -Command "Get-NetFirewallProfile"',
            "Recent Logins": 'powershell -Command "Get-EventLog -LogName Security -InstanceId 4624 -Newest 5"',
            "Users Logged In": 'query user',
            "System Integrity": 'sfc /scannow',
            "System Updates": 'powershell -Command "Get-WindowsUpdate"',
            "Active Services": 'powershell -Command "Get-Service | Where-Object {$_.Status -eq \'Running\'}"',
            "Antivirus Status": 'powershell -Command "Get-MpComputerStatus | Select-Object AMServiceEnabled,AntispywareEnabled,AntivirusEnabled,RealTimeProtectionEnabled"'
        }

    # Procesamiento en paralelo
    with ProcessPoolExecutor() as executor:
        future_to_key = {executor.submit(run_command, cmd): key for key, cmd in commands.items()}

        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                info[key] = future.result()
            except Exception as e:
                info[key] = f"Error ejecutando {key}: {e}"

    # Llamar temperatura separada si estás en Windows (porque es una función personalizada)
    if os_name == "Windows":
        info["CPU Temp"] = obtener_temperatura_cpu()

    return info

