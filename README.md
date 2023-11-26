# Team assignment 2


clone the reposetory
cd into reposetory

run command:
pip install -r requirements.txt

cd into WeatherForecast
use sodu docker compose up -d

cd back into project directory

cd into MotionCollision
use sodu docker compose up -d

cd back into project directory

cd into MQTT
use sodu docker compose up -d

add users to MQTT:
user1-password
user2-password
user3-password

cd back into project directory

cd into TrafficSubscriber
run command:
python3 DashboardFlask.py 

open a new consloe an cd into TrafficPublisher
run command:
python3 DashboardFlask.py 

