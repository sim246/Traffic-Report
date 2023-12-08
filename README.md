# Team assignment 2
Team: Simona Dragomir, Charles-Alexandre Bouchard

Project Title: Traffic Report

Project Overview: A system that runs on the Raspberry Pi that manages weather and motion collision data. It recives information from a publisher and displays the weather 
and the infractions after classifing then. It also verifies subscribers' validity using tokens and asynchronous  keys.

project Details: There in a Keys folder with a asymetric_keys that generates and keeps the keys. The MotionCollision and WeatherForecast folders contain the code which 
builds the apis (Docker files, Controllers), the MQTT folder contains the service that manages the publish/subscribe messageing services and, the TrafficPublisher and 
TrafficSubscriber folders contain the subscriber and publisher services. The Dashboard in the DashboardFlask also includes the subscriber code since it was simpler to have 
both the code for the dashboaard and the code that retreaves the data together in one file.

Follow these steps to set up the environment:

Clone the Repository:

    git clone [repository-url]
    cd [repository-name]

Install Dependencies:

    pip install -r requirements.txt

WeatherForecast Microservice:

    cd WeatherForecast
    sudo docker compose up -d

MotionCollision Microservice:

    cd ../MotionCollision
    sudo docker compose up -d

MQTT Microservice:

    cd ../MQTT
    sudo docker compose up -d

Add Users to MQTT:

    sudo docker exec -it mosquitto_broker sh
    mosquitto_passwd -c /mosquitto/config/passwd user1
    mosquitto_passwd /mosquitto/config/passwd user2
    mosquitto_passwd /mosquitto/config/passwd user3
    exit

    user1: password
    user2: password
    user3: password

TrafficSubscriber Microservice (on same or different raspberry pi):

    cd ../TrafficSubscriber
    python3 DashboardFlask.py (if on different raspberry change localhost to other raspberry's ip address)

TrafficPublisher Microservice:

    Open a new console

    cd TrafficPublisher
    python3 publisher.py

