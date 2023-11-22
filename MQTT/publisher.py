import time
import json
import paho.mqtt.client as mqtt
import requests
import sys

broker_hostname = "localhost"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client(client_id="Client1", userdata=None)
client.on_connect = on_connect

# change with your user and password auth
client.username_pw_set(username="user_name", password="password")


client.connect(broker_hostname, port, 60)
#client.loop_forever()
client.loop_start()

topic = "TODO"
msg = "TODO"

def make_request_weather():
    url = "http://0.0.0.0:5080/WeatherForecast"
    response = requests.get(url)
    response_json = response.json()
    #print(response_json)
    return response_json


def make_request_motioncollision():
    url = "http://0.0.0.0:5081/MotionCollisionSensorController"
    response = requests.get(url)
    response_json = response.json()
    #print(response_json)
    return response_json


msg_count = 0
try:
    while msg_count < 100:
        time.sleep(5)
        msg_count += 1
        
        topic = "WeatherForecast"
        msg = json.dumps(make_request_weather())
        result = client.publish(topic=topic, payload=msg)
        status = result[0]
        
        if status == 0:
            print("Message "+ msg + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
            
        topic = "CollisionSensor"
        msg = json.dumps(make_request_motioncollision())
        result = client.publish(topic=topic, payload=msg)
        status = result[0]
        
        if status == 0:
            print("Message "+ msg + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
finally:
    client.loop_stop()
