# Team assignment 2

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

