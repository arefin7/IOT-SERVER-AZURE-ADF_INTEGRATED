import paho.mqtt.client as mqtt
import json
import mysql.connector
from datetime import datetime

# ------------------- DB CONFIG --------------------
DB_HOST = "localhost"
DB_USER = "iotuser"
DB_PASSWORD = "mariadb"
DB_NAME = "tdb"

# ------------------- DB HANDLER -------------------
def insert_sensor_data(device_id, temperature, vibration, rpm, timestamp):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor()
        query = """
            INSERT INTO sensor_data (device_id, temperature, vibration, rpm, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (device_id, temperature, vibration, rpm, timestamp))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[✓] Inserted data for {device_id} at {timestamp}")
    except Exception as e:
        print(f"[×] DB Insert Error: {e}")

# ------------------- MQTT CALLBACKS -------------------
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code:", rc)
    client.subscribe("machine/+/data")
    print("Subscribed to topic: machine/+/data")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        device_id = topic_parts[1]

        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        temperature = float(data.get("temperature", 0))
        vibration = float(data.get("vibration", 0))
        rpm = int(data.get("rpm", 0))
        timestamp = data.get("timestamp")

        # Validate timestamp
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_sensor_data(device_id, temperature, vibration, rpm, timestamp)
    except Exception as e:
        print(f"[×] MQTT Message Handling Error: {e}")
        print(f"Payload: {msg.payload}")

# ------------------- MAIN -------------------
def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
