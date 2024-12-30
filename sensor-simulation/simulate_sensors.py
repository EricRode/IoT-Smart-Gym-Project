import paho.mqtt.client as mqtt
import random
import time
import json
import os
from datetime import datetime

# MQTT Configuration
broker = os.getenv("MQTT_BROKER", "mqtt_broker")
port = 1883
username = os.getenv("MQTT_USERNAME", "smart-gym")
password = os.getenv("MQTT_PASSWORD", "smartgym#2024")
topic = "/gym/sensors"

client = mqtt.Client()
client.username_pw_set(username, password)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker" if rc == 0 else f"Failed to connect, code {rc}")

client.on_connect = on_connect
client.connect(broker, port, keepalive=60)
client.loop_start()

# Simulation Function
def simulate_data():
    max_capacity = 50  # Max number of people in the gym
    occupancy = random.randint(0, max_capacity)
    equipment_count = 20  # Total gym equipment
    equipment_in_use = random.randint(0, equipment_count)

    while True:
        # Simulating various metrics
        data = {
            "timestamp": datetime.now().isoformat(),
            "air_quality": round(random.uniform(10, 100), 2),  # AQI value
            "occupancy": occupancy + random.choice([-1, 1]),  # +1/-1 occupancy change
            "temperature": round(random.uniform(18, 30), 1),  # in Celsius
            "humidity": round(random.uniform(30, 70), 1),  # percentage
            "noise_level": round(random.uniform(40, 90), 1),  # dB
            "equipment_status": {
                f"machine_{i}": random.choice(["OK", "In Use", "Needs Maintenance"])
                for i in range(1, equipment_count + 1)
            },
            "energy_usage": round(random.uniform(500, 1500), 2),  # watts
            "water_dispenser_usage": random.randint(0, 5),  # usage count
        }

        # Publish to MQTT
        result = client.publish(topic, json.dumps(data))
        if result.rc == 0:
            print(f"Published: {data}")
        else:
            print("Failed to publish message")

        time.sleep(5)  # Interval between readings

# Run Simulation
try:
    simulate_data()
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()