# 🚔 My SecureCheck Project Logs

A professional traffic stop analytics dashboard built using **Streamlit**, **Pandas**, and **SQLite**. This interactive data app allows users to filter historic check post logs, view dynamic operational graphs, add new verified log entries, and auto-predict incident outcomes based on historical trends.

## 🚀 Features
* **🔎 Dynamic Filters:** Filter records cleanly by violation type (`Speeding`, `Dui`, `Seatbelt`, etc.) and driver demographics.
* **📋 Digital Ledger:** Interactive tabular data view of active traffic log records.
* **📊 Analytics Charts:** Plotly charts visualizing age distributions against arrest statuses and violation outcome breakdowns.
* **📝 Predictive Log Entry:** A structured main form to save new field reports straight to the SQL database with auto-calculated citation/arrest warnings.

## ⚙️ How to Setup and Run
1. Install the required dependencies:
   ```bash
   pip install streamlit pandas plotly
   ```
2. Place your database file (`securecheck.db`) and CSV records (`traffic_stops.csv`) in the same root folder.
3. Launch the dashboard application via terminal:
   ```bash
   streamlit run securecheck.py
   ```
