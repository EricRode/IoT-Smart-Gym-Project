
# Smart Gym IoT System

## Setup
1. Install Docker and Docker Compose.
2. Clone this repository.
3. Run `docker-compose build`
4. Run `docker-compose up` to start all services.

## Components
- MQTT: Message broker for sensor communication.
- Node-RED: Middleware for processing data.
- InfluxDB: Storage for sensor data.
- Grafana: Dashboard for visualization.
- Sensor Simulator: Publishes mock data to MQTT.
