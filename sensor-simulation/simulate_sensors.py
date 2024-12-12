import paho.mqtt.client as mqtt
import time
import random
import json
import os

broker = os.getenv("MQTT_BROKER", "mqtt_broker")
port = 1883
username = os.getenv("MQTT_USERNAME", "myuser")
password = os.getenv("MQTT_PASSWORD", "mypassword")
topic = "/gym/sensors"

client = mqtt.Client()
client.username_pw_set(username, password)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

client.on_connect = on_connect

# Retry logic
while True:
    try:
        client.connect(broker, port, keepalive=60)
        break
    except ConnectionRefusedError:
        print("Connection refused. Retrying in 5 seconds...")
        time.sleep(5)

client.loop_start()

def publish_data():
    while True:
        data = {
            "occupancy": random.randint(0, 15),
            "temperature": round(random.uniform(18, 35), 1),
            "equipment_status": "OK" if random.random() > 0.1 else "Malfunction"
        }
        client.publish(topic, json.dumps(data))
        print(f"Published: {data}")
        time.sleep(5)

try:
    publish_data()
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()
