import mysql.connector
from datetime import datetime, timedelta

class MariaDBHandler:
    def __init__(self, host="localhost", user="iotuser", password="iotpassword", database="iot_data"):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(50),
                temperature FLOAT,
                vibration FLOAT,
                rpm INT,
                timestamp DATETIME
            )
        """)
        self.connection.commit()

    def insert_data(self, device_id, temperature, vibration, rpm, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        self.cursor.execute("""
            INSERT INTO sensor_data (device_id, temperature, vibration, rpm, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (device_id, temperature, vibration, rpm, timestamp))
        self.connection.commit()

    def get_avg_rpm_last_n_hours(self, n):
        query = """
            SELECT device_id, AVG(rpm) as avg_rpm
            FROM sensor_data
            WHERE timestamp >= NOW() - INTERVAL %s HOUR
            GROUP BY device_id
        """
        self.cursor.execute(query, (n,))
        return self.cursor.fetchall()

    def get_downtime_last_n_days(self, threshold_rpm, days):
        query = """
            SELECT device_id, COUNT(*) as downtime_count
            FROM sensor_data
            WHERE rpm < %s AND timestamp >= NOW() - INTERVAL %s DAY
            GROUP BY device_id
        """
        self.cursor.execute(query, (threshold_rpm, days))
        return self.cursor.fetchall()

    def get_readings_last_1_hour(self):
        query = """
            SELECT * FROM sensor_data
            WHERE timestamp >= NOW() - INTERVAL 1 HOUR
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_daily_avg_rpm(self):
        query = """
            SELECT DATE(timestamp) as date, device_id, AVG(rpm) as avg_rpm
            FROM sensor_data
            GROUP BY DATE(timestamp), device_id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_machine_utilization(self, min_rpm=800):
        query = """
            SELECT DATE(timestamp) as date, device_id,
            100.0 * SUM(CASE WHEN rpm >= %s THEN 1 ELSE 0 END) / COUNT(*) as utilization_percent
            FROM sensor_data
            GROUP BY DATE(timestamp), device_id
        """
        self.cursor.execute(query, (min_rpm,))
        return self.cursor.fetchall()

    def get_low_rpm_records(self, device_id, threshold_rpm=800):
        query = """
            SELECT timestamp, rpm
            FROM sensor_data
            WHERE rpm < %s AND device_id = %s
        """
        self.cursor.execute(query, (threshold_rpm, device_id))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
