# Team assignment 2


clone the repository
cd into repository

run commands:
pip install -r requirements.txt

cd WeatherForecast
sudo docker compose up -d

cd ../

cd MotionCollision
sudo docker compose up -d

cd ../

cd MQTT
sudo docker compose up -d

add users to MQTT:
user1-password
user2-password
user3-password

cd ../

cd TrafficSubscriber
run command:
python3 DashboardFlask.py 

open a new console and cd TrafficPublisher
run command:
python3 publisher.py 

