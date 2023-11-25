import json
import paho.mqtt.client as mqtt
import time

global weather_data, collision_data, public_key
weather_data = ""
motion_collision_data = ""

broker_hostname = "localhost"
port = 1883

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("WeatherForecast")
        client.subscribe("MotionCollisionSensor")
        #client.subscribe("PublicKey")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    global weather_data, collision_data, public_key
    print("Received message: ")
    if message.topic == "WeatherForecast":
        weather_data = json.loads(str(message.payload.decode("utf-8")))
        print(weather_data)
    elif message.topic == "MotionCollisionSensor":
        motion_collision_data = json.loads(str(message.payload.decode("utf-8")))
        print(motion_collision_data["date"] + motion_collision_data["postalCode"] + str(motion_collision_data["theDetection"]))
    #elif message.topic == "PublicKey":
        #public_key_data = json.loads(message.payload.decode("utf-8"))
        #public_key_bytes = base64.b64decode(public_key_data.get('publickey'))
        #public_key = serialization.load_pem_public_key(public_key_bytes)

def connect():
    client = mqtt.Client("Client3")
    client.username_pw_set(username="user1", password="password")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_hostname, port)
    client.loop_start()
    try:
        time.sleep(9999999)
    finally:
        client.loop_stop()

def get_weather():
    global weather_data
    if weather_data != "":
        return weather_data

def get_motion_collision():
    global collision_data
    if motion_collision_data != "":
        return motion_collision_data
