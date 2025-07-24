from flask import Flask, jsonify, request
from db_handler import MariaDBHandler
from config import Config

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.db = MariaDBHandler(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/")
        def home():
            return "Welcome to the IoT REST API"

        @self.app.route("/api/avg-rpm/<int:hours>")
        def avg_rpm(hours):
            data = self.db.get_avg_rpm_last_n_hours(hours)
            return jsonify(data)

        @self.app.route("/api/downtime/<int:days>")
        def downtime(days):
            data = self.db.get_downtime_last_n_days(threshold_rpm=800, days=days)
            return jsonify(data)

        @self.app.route("/api/last-hour")
        def last_hour():
            data = self.db.get_readings_last_1_hour()
            return jsonify(data)

        @self.app.route("/api/daily-avg-rpm")
        def daily_avg_rpm():
            data = self.db.get_daily_avg_rpm()
            return jsonify(data)

        @self.app.route("/api/utilization")
        def utilization():
            data = self.db.get_machine_utilization()
            return jsonify(data)

        @self.app.route("/api/low-rpm/<device_id>")
        def low_rpm(device_id):
            data = self.db.get_low_rpm_records(device_id=device_id)
            return jsonify(data)

    def run(self):
        self.app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    flask_app = FlaskApp()
    flask_app.run()
