# Team assignment 2

Project Title: Traffic Report

Project Overview: A system that runs on the Raspberry Pi that manages weather and motion collision data. It also classifies infractions and displays then on a UI. 

project Details: there is a Keys file that generates and keeps the keys. MotionCollision and WeatherForecast which build the apis, the MQTT that manages the publish/subscribe messageing service and, TrafficPublisher and TrafficSubscriber which are the subscriber and publisher.

Follow these steps to set up the environment:

Clone the Repository:

    git clone [repository-url]
    cd [repository-name]

Install Dependencies:

    pip install -r requirements.txt

WeatherForecast Microservice:

    cd WeatherForecast
    sudo docker-compose up -d

MotionCollision Microservice:

    cd ../MotionCollision
    sudo docker-compose up -d

MQTT Microservice:

    cd ../MQTT
    sudo docker-compose up -d

Add Users to MQTT:

    user1: password
    user2: password
    user3: password

TrafficSubscriber Microservice:

    cd ../TrafficSubscriber
    python3 DashboardFlask.py

TrafficPublisher Microservice:

    Open a new console

    cd TrafficPublisher
    python3 publisher.py

