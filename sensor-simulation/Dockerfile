FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install python-dotenv
ENV MQTT_USERNAME=smart-gym
ENV MQTT_PASSWORD=smartgym#2024
CMD ["python", "simulate_sensors.py"]
