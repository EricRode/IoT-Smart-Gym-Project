import paho.mqtt.client as mqtt
import random
import time
import json
import os
from datetime import datetime, timedelta

# MQTT Konfiguration
broker = os.getenv("MQTT_BROKER", "mqtt_broker")
port = 1883
username = os.getenv("MQTT_USERNAME", "smart-gym")
password = os.getenv("MQTT_PASSWORD", "smartgym#2024")
client = mqtt.Client()
client.username_pw_set(username, password)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker" if rc == 0 else f"Failed to connect, code {rc}")

client.on_connect = on_connect
client.connect(broker, port, keepalive=60)
client.loop_start()

# Gym Standorte mit Sensorenanzahl
mcfit_locations = [
    {
        "name": "McFIT Berlin-Stadtmitte",
        "abbreviation": "MBS",
        "coordinates": [52.5101, 13.3911],
        "sensor_counts": {
            "occupancy": 2,
            "temperature": 3,
            "humidity": 1,
            "co2_level": 2,
            "no2_level": 1,
            "noise_level": 2,
            "energy_usage": 1,
        }
    },
    {
        "name": "McFIT Berlin-Adlershof",
        "abbreviation": "MBA",
        "coordinates": [52.4368, 13.5341],
        "sensor_counts": {
            "occupancy": 3,
            "temperature": 2,
            "humidity": 2,
            "co2_level": 3,
            "no2_level": 2,
            "noise_level": 3,
            "energy_usage": 1,
        }
    },
    {
        "name": "McFIT Berlin-Lichterfelde",
        "abbreviation": "MBL",
        "coordinates": [52.4333, 13.2944],
        "sensor_counts": {
            "occupancy": 2,
            "temperature": 1,
            "humidity": 1,
            "co2_level": 1,
            "no2_level": 1,
            "noise_level": 1,
            "energy_usage": 2,
        }
    },
    {
        "name": "McFIT Berlin-Lichtenberg",
        "abbreviation": "MBLN",
        "coordinates": [52.5144, 13.4906],
        "sensor_counts": {
            "occupancy": 4,
            "temperature": 3,
            "humidity": 2,
            "co2_level": 3,
            "no2_level": 2,
            "noise_level": 2,
            "energy_usage": 1,
        }
    },
    {
        "name": "McFIT Berlin-Charlottenburg",
        "abbreviation": "MBC",
        "coordinates": [52.5036, 13.3415],
        "sensor_counts": {
            "occupancy": 1,
            "temperature": 2,
            "humidity": 2,
            "co2_level": 2,
            "no2_level": 1,
            "noise_level": 3,
            "energy_usage": 2,
        }
    },
]

# Eindeutige IDs für alle Sensoren erstellen
for location in mcfit_locations:
    abbreviation = location["abbreviation"]
    location["sensors"] = {}
    for sensor_type, count in location["sensor_counts"].items():
        location["sensors"][sensor_type] = [
            f"sensor_{abbreviation}_{sensor_type}_{i+1}" for i in range(count)
        ]

# Beschleunigter Modus für die Simulation
TIME_ACCELERATED_MODE = True  # Setze auf False für Echtzeitsimulation
SCALING_FACTOR = 5  # Skaliere die Belegung auf größere Werte

def get_time_based_occupancy(simulated_hour):
    """Belegung basierend auf der simulierten Zeit berechnen."""
    base_occupancy = 0
    fluctuation = random.randint(-5, 5)  # Kleine Schwankung um den Basiswert
    
    if 6 <= simulated_hour < 9:  # Morgenrush
        base_occupancy = 40
    elif 9 <= simulated_hour < 12:  # Vormittag
        base_occupancy = 25
    elif 12 <= simulated_hour < 15:  # Früher Nachmittag
        base_occupancy = 10
    elif 15 <= simulated_hour < 20:  # Abendrush
        base_occupancy = 40
    elif 20 <= simulated_hour < 24:  # Später Abend
        base_occupancy = 20
    else:  # Nacht (00:00 - 06:00)
        base_occupancy = 0

    return max(0, (base_occupancy + fluctuation) * SCALING_FACTOR)

def get_co2_level(occupancy):
    """CO2-Wert basierend auf der Belegung simulieren."""
    base_co2 = 400  # Durchschnittlicher CO2-Wert im Freien (ppm)
    return round(base_co2 + (occupancy * random.uniform(5, 10)), 2)

def get_no2_level(occupancy):
    """NO2-Wert basierend auf der Belegung simulieren."""
    base_no2 = 20  # Basiswert für NO2 (ppb)
    return round(base_no2 + (occupancy * random.uniform(0.2, 0.5)), 2)

def get_pm25_level(occupancy):
    """PM2.5 value based on occupancy."""
    base_pm25 = 5  # Average outdoor PM2.5 level in µg/m³
    return round(base_pm25 + (occupancy * random.uniform(0.5, 1.0)), 2)

def get_pm10_level(occupancy):
    """PM10 value based on occupancy."""
    base_pm10 = 10  # Average outdoor PM10 level in µg/m³
    return round(base_pm10 + (occupancy * random.uniform(1.0, 2.0)), 2)

# Update the sensor simulation
def simulate_data():
    simulated_time = datetime.now() if not TIME_ACCELERATED_MODE else datetime(2022, 1, 1, 0, 0, 0)

    while True:
        if TIME_ACCELERATED_MODE:
            simulated_time += timedelta(seconds=1)  # 1 second = 1 minute
            simulated_hour = simulated_time.hour
        else:
            simulated_hour = datetime.now().hour

        for location in mcfit_locations:
            abbreviation = location["abbreviation"]
            occupancy = get_time_based_occupancy(simulated_hour)

            for sensor_type, sensors in location["sensors"].items():
                for sensor_id in sensors:
                    # Generate sensor data based on type
                    value = None
                    if sensor_type == "occupancy":
                        value = occupancy
                    elif sensor_type == "temperature":
                        value = round(random.uniform(18, 30), 1)
                    elif sensor_type == "humidity":
                        value = round(random.uniform(30, 70), 1)
                    elif sensor_type == "co2_level":
                        value = get_co2_level(occupancy)
                    elif sensor_type == "no2_level":
                        value = get_no2_level(occupancy)
                    elif sensor_type == "noise_level":
                        value = round(random.uniform(40, 90), 1)
                    elif sensor_type == "pm2.5":
                        value = get_pm25_level(occupancy)
                    elif sensor_type == "pm10":
                        value = get_pm10_level(occupancy)

                    # Publish data for each sensor
                    if value is not None:
                        topic = f"/smartgym/{abbreviation}/{sensor_type}"
                        payload = {
                            "timestamp": simulated_time.isoformat(),
                            "location": location["name"],
                            "coordinates": location["coordinates"],
                            "sensor_id": sensor_id,
                            "value": value,
                        }
                        result = client.publish(topic, json.dumps(payload))
                        if result.rc == 0:
                            print(f"Published to {topic}: {payload}")
                        else:
                            print(f"Failed to publish to {topic}")

        time.sleep(10 if TIME_ACCELERATED_MODE else 20)

# Simulation starten
try:
    simulate_data()
except KeyboardInterrupt:
    print("Simulation gestoppt.")
finally:
    client.loop_stop()
    client.disconnect()