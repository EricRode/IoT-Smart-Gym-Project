
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

## Telegram
To implement the telegram bot it is necessary to create the credentials for the bot.
1. Go to telegram and start a chat with @BotFather
2. Answer the questions and save the generated token
3. Create two groups: 
    - admin group
    - normal group for messages  
4. Invite your bot to both groups
5. Add the bot @getmyid_bot to both groups
6. Obtain the chatIds for both chats
7. Remove the @getmyid_bot
8. Finally, put the chatIds and the bot token in the .env file