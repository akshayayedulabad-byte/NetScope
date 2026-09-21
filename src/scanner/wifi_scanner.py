import subprocess
import re
from datetime import datetime

def scan_wifi_networks():
    """
    Scans nearby Wi-Fi networks using Windows netsh command
    and returns a list of dictionaries containing network details.
    """
    try:
        # Run the Windows command to show Wi-Fi networks with BSSID details
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        output = result.stdout

        if not output:
            print("No output received from netsh. Make sure Wi-Fi is turned ON.")
            return []

        networks = []
        current_network = {}

        # Split the output into lines and process one by one
        lines = output.splitlines()

        for line in lines:
            line = line.strip()

            # Detect SSID (network name)
            if line.startswith("SSID") and "BSSID" not in line:
                # Save previous network if it exists
                if current_network and "ssid" in current_network:
                    networks.append(current_network)

                # Start a new network entry
                ssid_match = re.search(r"SSID\s+\d+\s+:\s+(.*)", line)
                if ssid_match:
                    current_network = {
                        "ssid": ssid_match.group(1).strip(),
                        "bssid": None,
                        "signal": None,
                        "channel": None,
                        "frequency": None,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

            # Detect BSSID (MAC address of access point)
            elif "BSSID" in line:
                bssid_match = re.search(r"BSSID\s+\d+\s+:\s+([0-9A-Fa-f:]+)", line)
                if bssid_match and current_network:
                    current_network["bssid"] = bssid_match.group(1).strip()

            # Detect Signal strength
            elif "Signal" in line:
                signal_match = re.search(r"Signal\s+:\s+(\d+)%", line)
                if signal_match and current_network:
                    # Convert percentage to approximate RSSI (dBm)
                    # Windows gives %, we convert roughly to dBm for consistency
                    percent = int(signal_match.group(1))
                    # Common approximate conversion: 100% ≈ -50 dBm, 0% ≈ -100 dBm
                    rssi = -100 + (percent // 2)
                    current_network["signal"] = rssi
                    current_network["signal_percent"] = percent

            # Detect Channel
            elif "Channel" in line:
                channel_match = re.search(r"Channel\s+:\s+(\d+)", line)
                if channel_match and current_network:
                    channel = int(channel_match.group(1))
                    current_network["channel"] = channel
                    # Approximate frequency (2.4 GHz or 5 GHz)
                    if channel <= 14:
                        current_network["frequency"] = "2.4 GHz"
                    else:
                        current_network["frequency"] = "5 GHz"

        # Don't forget to add the last network
        if current_network and "ssid" in current_network:
            networks.append(current_network)

        return networks

    except Exception as e:
        print(f"Error while scanning Wi-Fi: {e}")
        return []


def print_networks(networks):
    """Nicely print the scanned networks."""
    if not networks:
        print("\nNo Wi-Fi networks found.")
        print("Possible reasons:")
        print("  - Wi-Fi is turned OFF")
        print("  - No networks in range")
        print("  - Adapter does not support scanning")
        return

    print(f"\nFound {len(networks)} Wi-Fi network(s):\n")
    print("-" * 80)
    print(f"{'SSID':<25} {'BSSID':<20} {'Signal':<12} {'Channel':<10} {'Freq'}")
    print("-" * 80)

    for net in networks:
        ssid = net.get("ssid", "Unknown")[:24]
        bssid = net.get("bssid", "N/A")
        signal = f"{net.get('signal', 'N/A')} dBm" if net.get("signal") else "N/A"
        channel = str(net.get("channel", "N/A"))
        freq = net.get("frequency", "N/A")

        print(f"{ssid:<25} {bssid:<20} {signal:<12} {channel:<10} {freq}")

    print("-" * 80)
    print(f"Scan time: {networks[0]['timestamp'] if networks else 'N/A'}")


# This part runs only when you execute the file directly
if __name__ == "__main__":
    print("Scanning nearby Wi-Fi networks... Please wait.")
    networks = scan_wifi_networks()
    print_networks(networks)