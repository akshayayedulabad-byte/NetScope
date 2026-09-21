import sqlite3
import os
from datetime import datetime

# Path to the database file
DB_PATH = os.path.join("data", "netscope.db")


def get_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn


def create_tables():
    """
    Create the required tables if they do not already exist.
    This function is safe to run multiple times.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table to store every Wi-Fi measurement
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ssid TEXT,
            bssid TEXT,
            signal_dbm INTEGER,
            signal_percent INTEGER,
            channel INTEGER,
            frequency TEXT,
            x REAL,
            y REAL,
            timestamp TEXT,
            notes TEXT
        )
    """)

    # Table to store floor plan information (for future use)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS floorplans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            width INTEGER,
            height INTEGER,
            uploaded_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables created successfully (or already exist).")


def insert_measurement(ssid, bssid, signal_dbm, signal_percent, channel,
                       frequency, x, y, notes=""):
    """
    Insert one Wi-Fi measurement into the database.
    Returns the ID of the newly inserted row.
    """
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO measurements 
        (ssid, bssid, signal_dbm, signal_percent, channel, frequency, x, y, timestamp, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ssid, bssid, signal_dbm, signal_percent, channel, frequency, x, y, timestamp, notes))

    measurement_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return measurement_id


def get_all_measurements():
    """Return all measurements as a list of dictionaries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM measurements ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to normal Python dictionaries
    return [dict(row) for row in rows]


def get_measurements_by_ssid(ssid):
    """Return measurements filtered by a specific SSID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM measurements WHERE ssid = ? ORDER BY timestamp DESC", (ssid,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_all_measurements():
    """Delete all measurements (useful for testing)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM measurements")
    conn.commit()
    conn.close()
    print("All measurements have been deleted.")


# This part runs only when you execute the file directly
if __name__ == "__main__":
    print("Setting up NetScope database...")
    create_tables()

    # Insert one sample measurement so we can test
    sample_id = insert_measurement(
        ssid="Test_Network",
        bssid="00:11:22:33:44:55",
        signal_dbm=-65,
        signal_percent=70,
        channel=6,
        frequency="2.4 GHz",
        x=150.0,
        y=220.0,
        notes="Sample data for testing"
    )
    print(f"Sample measurement inserted with ID: {sample_id}")

    # Read and show all measurements
    all_data = get_all_measurements()
    print(f"\nTotal measurements in database: {len(all_data)}")
    for row in all_data:
        print(row)