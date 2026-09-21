import sys
import os

# Add the project root to Python path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scanner.wifi_scanner import scan_wifi_networks, print_networks
from src.database.db_manager import create_tables, insert_measurement, get_all_measurements


def collect_and_save():
    """
    1. Scan nearby Wi-Fi networks
    2. Ask user for current location (X, Y)
    3. Save every network found into the database
    """
    print("=" * 60)
    print("       NetScope – Data Collection Mode")
    print("=" * 60)

    # Make sure tables exist
    create_tables()

    # Step 1: Scan Wi-Fi
    print("\nScanning nearby Wi-Fi networks... Please wait.")
    networks = scan_wifi_networks()
    print_networks(networks)

    if not networks:
        print("\nNo networks found. Cannot save data.")
        return

    # Step 2: Ask for location
    print("\n" + "-" * 60)
    print("Enter your current location on the floor plan.")
    print("Use simple numbers for now (example: X = 150, Y = 220)")
    print("-" * 60)

    try:
        x = float(input("Enter X coordinate: "))
        y = float(input("Enter Y coordinate: "))
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return

    notes = input("Optional notes (press Enter to skip): ").strip()

    # Step 3: Save every network into the database
    print("\nSaving measurements to database...")
    saved_count = 0

    for net in networks:
        # Some networks may miss certain fields, so we use .get() safely
        insert_measurement(
            ssid=net.get("ssid", "Unknown"),
            bssid=net.get("bssid"),
            signal_dbm=net.get("signal"),
            signal_percent=net.get("signal_percent"),
            channel=net.get("channel"),
            frequency=net.get("frequency"),
            x=x,
            y=y,
            notes=notes
        )
        saved_count += 1

    print(f"\nSuccessfully saved {saved_count} measurement(s) at location ({x}, {y}).")

    # Show how many total records are now in the database
    all_data = get_all_measurements()
    print(f"Total measurements currently in database: {len(all_data)}")


if __name__ == "__main__":
    collect_and_save()