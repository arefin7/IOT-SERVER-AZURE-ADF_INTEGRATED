import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

class Dashboard:
    def __init__(self):
        self.base_url = "http://localhost:5000"

    def get_avg_rpm(self, hours):
        response = requests.get(f"{self.base_url}/average_rpm", params={"hours": hours})
        return response.json()

    def get_downtime(self, days):
        response = requests.get(f"{self.base_url}/downtime", params={"days": days})
        return response.json()

    def get_last_hour_data(self):
        response = requests.get(f"{self.base_url}/last_hour_readings")
        return response.json()

    def get_daily_avg_rpm(self):
        response = requests.get(f"{self.base_url}/daily_avg_rpm")
        return response.json()

    def get_utilization(self):
        response = requests.get(f"{self.base_url}/utilization")
        return response.json()

    def get_rpm_below_threshold(self, threshold, machine_id):
        response = requests.get(f"{self.base_url}/rpm_below_threshold", params={"threshold": threshold, "machine_id": machine_id})
        return response.json()

    def run(self):
        st.title("Industrial IoT Dashboard")

        st.header("1. Average RPM of Last N Hours")
        hours = st.slider("Select Hours", 1, 48, 4)
        avg_rpm = self.get_avg_rpm(hours)
        st.json(avg_rpm)

        st.header("2. Downtime of N Days")
        days = st.slider("Select Days", 1, 30, 7)
        downtime = self.get_downtime(days)
        st.json(downtime)

        st.header("3. Readings from Last 1 Hour")
        last_hour_data = self.get_last_hour_data()
        st.dataframe(pd.DataFrame(last_hour_data))

        st.header("4. Daily Average RPM of Different Devices")
        daily_avg_rpm = self.get_daily_avg_rpm()
        st.dataframe(pd.DataFrame(daily_avg_rpm))

        st.header("5. Machine Utilization Percentage per Day")
        utilization = self.get_utilization()
        st.dataframe(pd.DataFrame(utilization))

        st.header("6. RPM < 800 by Machine")
        threshold = 800
        machine_id = st.selectbox("Select Machine", ["loom1", "loom2"])
        low_rpm = self.get_rpm_below_threshold(threshold, machine_id)
        st.dataframe(pd.DataFrame(low_rpm))

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
