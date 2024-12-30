import paho.mqtt.client as mqtt
import time
import random
import json
import os

broker = os.getenv("MQTT_BROKER", "mqtt_broker")
port = 1883
username = os.getenv("MQTT_USERNAME", "smart-gym")
password = os.getenv("MQTT_PASSWORD", "smartgym#2024")
topic = "/gym/sensors"

print(f"Connecting to MQTT Broker at {broker}:{port} with username '{username}' and password '{password}'")

client = mqtt.Client()
client.username_pw_set(username, password)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT Broker with return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# Retry logic
while True:
    try:
        print("Attempting to connect to the broker...")
        client.connect(broker, port, keepalive=60)
        print("Connection successful")
        break
    except ConnectionRefusedError as e:
        print(f"Connection refused: {e}. Retrying in 5 seconds...")
        time.sleep(5)
    except Exception as e:
        print(f"Unexpected error: {e}. Retrying in 5 seconds...")
        time.sleep(5)

client.loop_start()

def publish_data():
    while True:
        data = {
            "occupancy": random.randint(0, 15),
            "temperature": round(random.uniform(18, 35), 1),
            "equipment_status": "OK" if random.random() > 0.1 else "Malfunction"
        }
        result = client.publish(topic, json.dumps(data))
        status = result.rc
        if status == 0:
            print(f"Published: {data}")
        else:
            print(f"Failed to send message to topic {topic}")
        time.sleep(5)

try:
    publish_data()
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()
