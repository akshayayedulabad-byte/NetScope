import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import insert_measurement, create_tables

create_tables()

locations = [
    (100, 100),
    (200, 150),
    (316, 208),
    (400, 250),
    (500, 300),
    (600, 180),
    (250, 350),
    (450, 400),
    (700, 350),
    (150, 450)
]

networks = [
    ("College_WiFi", "AA:BB:CC:DD:EE:01", 6, "2.4 GHz"),
    ("College_WiFi_5G", "AA:BB:CC:DD:EE:02", 36, "5 GHz"),
    ("Hostel_WiFi", "AA:BB:CC:DD:EE:03", 11, "2.4 GHz")
]

for i in range(30):
    x, y = random.choice(locations)
    ssid, bssid, channel, frequency = random.choice(networks)

    signal_dbm = random.randint(-90, -40)
    signal_percent = random.randint(10, 100)

    insert_measurement(
        ssid=ssid,
        bssid=bssid,
        signal_dbm=signal_dbm,
        signal_percent=signal_percent,
        channel=channel,
        frequency=frequency,
        x=x,
        y=y,
        notes="Synthetic data for project demonstration"
    )

print("30 synthetic Wi-Fi measurements added successfully!")