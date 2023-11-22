import time
import json
import paho.mqtt.client as mqtt
import requests

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
client.loop_start()

def make_request_weather():
    url = "http://0.0.0.0:5080/WeatherForecast"
    response = requests.get(url)
    response_json = response.json()
    return response_json

def make_request_motioncollision():
    url = "http://0.0.0.0:5081/CollisionSensor"
    response = requests.get(url)
    response_json = response.json()
    return response_json

def publish_weather_and_collision():
    msg_count = 0
    try:
        while msg_count < 100:
            time.sleep(5)
            msg_count += 1

            topic = "Weather"
            msg = json.dumps(make_request_weather())
            result = client.publish(topic=topic, payload=msg)
            status = result[0]

            if status == 0:
                print("Message " + msg + " is published to topic " + topic)
            else:
                print("Failed to send message to topic " + topic)

            topic = "MotionCollision"
            msg = json.dumps(make_request_motioncollision())
            result = client.publish(topic=topic, payload=msg)
            status = result[0]

            if status == 0:
                print("Message " + msg + " is published to topic " + topic)
            else:
                print("Failed to send message to topic " + topic)
    finally:
        client.loop_stop()

if __name__ == '__main__':
    publish_weather_and_collision()