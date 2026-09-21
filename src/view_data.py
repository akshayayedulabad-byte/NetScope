import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.db_manager import get_all_measurements, get_measurements_by_ssid


def view_all_data():
    """Display all measurements stored in the database in a clean table."""
    print("=" * 70)
    print("           NetScope – View Collected Measurements")
    print("=" * 70)

    data = get_all_measurements()

    if not data:
        print("\nNo measurements found in the database.")
        print("Please run the data collection script first.")
        return

    # Convert to pandas DataFrame for nice display
    df = pd.DataFrame(data)

    # Select and reorder important columns
    columns_to_show = [
        "id", "ssid", "bssid", "signal_dbm", "signal_percent",
        "channel", "frequency", "x", "y", "timestamp", "notes"
    ]

    # Keep only columns that actually exist
    columns_to_show = [col for col in columns_to_show if col in df.columns]
    df = df[columns_to_show]

    print(f"\nTotal measurements: {len(df)}\n")
    print(df.to_string(index=False))

    # Show quick statistics
    print("\n" + "-" * 70)
    print("Quick Statistics:")
    print(f"  Strongest signal : {df['signal_dbm'].max()} dBm")
    print(f"  Weakest signal   : {df['signal_dbm'].min()} dBm")
    print(f"  Average signal   : {df['signal_dbm'].mean():.1f} dBm")
    print(f"  Unique networks  : {df['ssid'].nunique()}")
    print("-" * 70)


def view_by_network():
    """Filter and show measurements of one specific network."""
    ssid = input("\nEnter the exact SSID (network name) to filter: ").strip()

    data = get_measurements_by_ssid(ssid)

    if not data:
        print(f"\nNo measurements found for network: {ssid}")
        return

    df = pd.DataFrame(data)
    print(f"\nMeasurements for '{ssid}': {len(df)} records\n")
    print(df[["id", "signal_dbm", "x", "y", "timestamp"]].to_string(index=False))


def main():
    while True:
        print("\n" + "=" * 40)
        print("1. View ALL measurements")
        print("2. Filter by network (SSID)")
        print("3. Exit")
        print("=" * 40)

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            view_all_data()
        elif choice == "2":
            view_by_network()
        elif choice == "3":
            print("Exiting viewer.")
            break
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    main()