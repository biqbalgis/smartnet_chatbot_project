import psutil
import socket
import speedtest
import subprocess
import platform
import requests
import time

def get_isp_from_ip():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        return data.get("org", "Unknown ISP")
    except Exception as e:
        return f"Unknown ISP (lookup failed: {str(e)})"

def diagnose_smartnet():
    try:
        # 1. Detect ISP via public IP
        isp = get_isp_from_ip()
        isp_lower = isp.lower()

        # ✅ Treat PTCL, SmartNet, or Pakistan Telecommunication as SmartNet
        if any(x in isp_lower for x in ["ptcl", "smartnet", "pakistan telecommunication"]):
            label = "SmartNet (PTCL)"
        else:
            return f"""🚫 You appear to be on a non-SmartNet network.
We’ve logged your complaint for further support.

**Detected ISP:** `{isp}`"""

        # 2. SSID Check (optional)
        ssid_info = subprocess.check_output("netsh wlan show interfaces", shell=True).decode("utf-8")
        if "State" not in ssid_info:
            return "⚠️ No active Wi-Fi interface found. Please check your wireless adapter."

        # 3. Speed Test
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / 1_000_000, 2)
        upload_speed = round(st.upload() / 1_000_000, 2)

        # 4. Ping Test
        if platform.system() == "Windows":
            ping_result = subprocess.check_output("ping -n 1 8.8.8.8", shell=True).decode("utf-8")
        else:
            ping_result = subprocess.check_output("ping -c 1 8.8.8.8", shell=True).decode("utf-8")

        # 5. Connected Devices
        connected_devices = len(psutil.net_connections())

        return f"""
📶 **Connected to {label}**

🔹 **ISP Detected:** `{isp}`
🔽 **Download Speed:** {download_speed} Mbps  
🔼 **Upload Speed:** {upload_speed} Mbps  
📡 **Ping Result:**
{ping_result.strip()}

📱 **Estimated Connected Devices:** {connected_devices}
"""
    except Exception as e:
        return f"❌ Diagnostic failed: {str(e)}"
