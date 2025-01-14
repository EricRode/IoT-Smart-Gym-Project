import paho.mqtt.client as mqtt
import random
import time
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


# MQTT Configuration
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

# Gym locations with the number of sensors
mcfit_locations = [
    {
        "name": "Olympus_Gym",
        "sensor_counts": {
            "temperature": 3,
            "humidity": 1,
            "co2_level": 2,
            "no2_level": 1,
            "noise_level": 2,
            "utilization": 1,
            "pm2.5": 1,
            "pm10": 1,
            "co_level": 1,
        }
    },
    {
        "name": "High_Tech_Gym",
        "sensor_counts": {
            "temperature": 2,
            "humidity": 2,
            "co2_level": 3,
            "no2_level": 2,
            "noise_level": 3,
            "utilization": 1,
            "pm2.5": 1,
            "pm10": 1,
            "co_level": 1,
        }
    },
    {
        "name": "Eagle_Fitness_Center",
        "sensor_counts": {
            "temperature": 1,
            "humidity": 1,
            "co2_level": 1,
            "no2_level": 1,
            "noise_level": 1,
            "utilization": 1,
            "pm2.5": 1,
            "pm10": 1,
            "co_level": 1,
        }
    },
    {
        "name": "Fit4Fun",
        "sensor_counts": {
            "temperature": 3,
            "humidity": 2,
            "co2_level": 3,
            "no2_level": 2,
            "noise_level": 2,
            "utilization": 1,
            "pm2.5": 1,
            "pm10": 1,
            "co_level": 1,
        }
    },
    {
        "name": "Sporting_Center",
        "sensor_counts": {
            "temperature": 2,
            "humidity": 2,
            "co2_level": 2,
            "no2_level": 1,
            "noise_level": 3,
            "utilization": 1,
            "pm2.5": 1,
            "pm10": 1,
            "co_level": 1,
        }
    },
]

# Generate unique IDs for all sensors
for location in mcfit_locations:
    name = location["name"]
    location["sensors"] = {}
    for sensor_type, count in location["sensor_counts"].items():
        location["sensors"][sensor_type] = [
            f"sensor_{name}_{sensor_type}_{i+1}" for i in range(count)
        ]

# Accelerated mode for simulation
TIME_ACCELERATED_MODE = True  # Set to False for real-time simulation
SCALING_FACTOR = 2  # Scale occupancy to higher values

def get_time_based_occupancy(simulated_hour):
    load_dotenv()
    max_occupancy = int(os.getenv("MAXIMUM_OCCUPANCY", 100))  # Default to 100 if not set

    """Calculate occupancy based on the simulated time."""
    base_occupancy = 0
    fluctuation = random.randint(-20, 20)  # Slight fluctuation around the base

    if 6 <= simulated_hour < 9:  # Morning rush
        base_occupancy = 50
    elif 9 <= simulated_hour < 12:  # Late morning
        base_occupancy = 20
    elif 12 <= simulated_hour < 15:  # Early afternoon
        base_occupancy = 30
    elif 15 <= simulated_hour < 20:  # Evening rush
        base_occupancy = 95
    elif 20 <= simulated_hour < 24:  # Late evening
        base_occupancy = 70
    else:  # Night (00:00 - 06:00)
        base_occupancy = 5

    # Cap the occupancy using the maximum value from the environment
    return min(max_occupancy, max(0, (base_occupancy + fluctuation)))

def get_co2_level(occupancy):
    """Simulate CO2 level based on occupancy."""
    base_co2 = 400  # Approx. outdoor CO2 (ppm)
    return round(base_co2 + (occupancy * random.uniform(5, 10)), 2)

def get_co_level(occupancy):
    base_co = 0.1  # Approximate outdoor CO concentration in ppm
    co_emission_per_person = random.uniform(0.00001, 0.00005)  # Randomized CO emission rate per person in ppm

    # Total CO emission from all occupants
    total_co_emission = occupancy * co_emission_per_person

    # Simulated indoor CO concentration
    indoor_co = base_co + total_co_emission

    return round(indoor_co, 4)

def get_no2_level(occupancy):
    """Simulate NO2 level based on occupancy."""
    base_no2 = 20  # Base NO2 (ppb)
    return round(base_no2 + (occupancy * random.uniform(0.2, 0.5)), 2)

def get_pm25_level(occupancy):
    """PM2.5 value based on occupancy."""
    base_pm25 = 5  # Average outdoor PM2.5 in µg/m³
    return round(base_pm25 + (occupancy * random.uniform(0.5, 1.0)), 2)

def get_pm10_level(occupancy):
    """PM10 value based on occupancy."""
    base_pm10 = 10  # Average outdoor PM10 in µg/m³
    return round(base_pm10 + (occupancy * random.uniform(1.0, 2.0)), 2)


def get_people_distribution(total_occupancy):
    """
    Reads area capacities from the .env file and distributes the total occupancy
    into specified areas based on their capacities.

    Args:
        total_occupancy (int): The total number of people.

    Returns:
        dict: A dictionary with area names as keys and the number of people distributed as values.
    """
    # Load the .env file
    load_dotenv()

    try:
        # Parse area capacities directly from the .env file
        area_capacities = {
            "strength_training": int(os.getenv("MAX_STRENGTH", 10)),
            "aerobic": int(os.getenv("MAX_AEROBIC", 10)),
            "functional": int(os.getenv("MAX_FUNCTIONAL", 10)),
            "no_equipment": int(os.getenv("MAX_NO_EQUIPMENT", 10)),
        }
    except ValueError as e:
        raise ValueError(f"Invalid values in the .env file: {e}")

    # Ensure total capacity is valid
    total_capacity = sum(area_capacities.values())
    if total_capacity == 0:
        raise ValueError("Total capacity in the .env file must be greater than 0.")

    # Initialize the distribution dictionary
    distribution = {area: 0 for area in area_capacities}

    # Proportional distribution
    for area, capacity in area_capacities.items():
        distribution[area] = int((capacity / total_capacity) * total_occupancy)

    # Handle remaining individuals due to rounding
    allocated = sum(distribution.values())
    remaining = total_occupancy - allocated
    areas = list(area_capacities.keys())
    for _ in range(remaining):
        area = random.choice(areas)
        distribution[area] += 1

    return distribution

def simulate_data():
    """Main loop to simulate and publish sensor data."""
    simulated_time = datetime.now() 

    while True:
        if TIME_ACCELERATED_MODE:
            # 1 second of real time = 1 minute of simulated time
            simulated_time += timedelta(seconds=1)
            simulated_hour = simulated_time.hour
        else:
            simulated_hour = datetime.now().hour

        for location in mcfit_locations:
            name = location["name"]
            occupancy = get_time_based_occupancy(simulated_hour)

            for sensor_type, sensors in location["sensors"].items():
                for sensor_id in sensors:
                    value = None

                    if sensor_type == "temperature":
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
                    elif sensor_type == "co_level":
                        value = get_co_level(occupancy)
                    elif sensor_type == "utilization":
                        # Get the dictionary of distribution and publish each key/value separately.
                        distribution_dict = get_people_distribution(occupancy)

                        for dist_key, dist_val in distribution_dict.items():
                            dist_topic = f"/smartgym/{name}/{dist_key}"
                            dist_payload = {
                                "timestamp": simulated_time.isoformat(),
                                "sensor_id": sensor_id,
                                "value": dist_val,
                            }
                            result = client.publish(dist_topic, json.dumps(dist_payload))
                            if result.rc == 0:
                                print(f"Published to {dist_topic}: {dist_payload}")
                            else:
                                print(f"Failed to publish to {dist_topic}")
                        # After publishing distribution, we can skip the single publish below
                        continue  # Skip the default publish step

                    # Publish data if we have a single value (for non-utilization sensors)
                    if value is not None:
                        topic = f"/smartgym/{name}/{sensor_type}"
                        payload = {
                            "timestamp": simulated_time.isoformat(),
                            "sensor_id": sensor_id,
                            "value": value,
                        }
                        result = client.publish(topic, json.dumps(payload))
                        if result.rc == 0:
                            print(f"Published to {topic}: {payload}")
                        else:
                            print(f"Failed to publish to {topic}")

        # Sleep before next iteration
        time.sleep(10 if TIME_ACCELERATED_MODE else 20)

# Start simulation
try:
    simulate_data()
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()