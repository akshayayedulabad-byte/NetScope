\# NetScope 📡



\## Intelligent Indoor Wi-Fi Coverage \& Dead-Zone Mapping System



NetScope is an indoor Wi-Fi monitoring and visualization system designed to collect Wi-Fi network information, associate measurements with physical locations, store the data, and visualize Wi-Fi coverage on a floor map.



The system helps identify weak-signal areas and potential Wi-Fi dead zones through heatmaps, statistics, and historical network analysis.



\## Features



\- 📡 Wi-Fi network scanning

\- 📍 Location-based measurement collection

\- 💾 SQLite database for storing measurements

\- 🗺️ Interactive floor-plan visualization

\- 🌡️ Wi-Fi signal-strength heatmap

\- ⚠️ Weak-signal and potential dead-zone identification

\- 📊 Statistics and network analysis

\- 📈 Historical network filtering and analysis

\- 📥 CSV data export

\- 🖥️ Streamlit-based dashboard



\## Technology Stack



\- \*\*Programming Language:\*\* Python

\- \*\*Dashboard:\*\* Streamlit

\- \*\*Database:\*\* SQLite

\- \*\*Data Processing:\*\* Pandas, NumPy

\- \*\*Visualization:\*\* Plotly

\- \*\*Image Processing:\*\* Pillow, OpenCV

\- \*\*Interpolation \& Analysis:\*\* SciPy

\- \*\*Location Selection:\*\* Streamlit Image Coordinates

\- \*\*Wi-Fi Scanning:\*\* Windows `netsh` WLAN utility



\## System Workflow



```text

Wi-Fi Networks

&#x20;     ↓

Wi-Fi Scanner

&#x20;     ↓

Location Selection

&#x20;     ↓

SQLite Database

&#x20;     ↓

Data Analysis

&#x20;     ↓

Heatmap \& Statistics

&#x20;     ↓

Streamlit Dashboard

## Data Collected

\- SSID

\- BSSID

\- Signal strength

\- Signal percentage

\- Channel

\- Frequency

\- Timestamp

\- X and Y location

\- Notes



NetScope/

│

├── data/

│   ├── floorplans/

│   └── exports/

│

├── src/

│   ├── scanner/

│   ├── database/

│   ├── analysis/

│   ├── visualization/

│   └── dashboard/

│

├── tests/

├── docs/

├── requirements.txt

└── README.md

