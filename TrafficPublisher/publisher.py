import base64
import requests
import json
import jwt
import time
import datetime
from random import randrange
from picamera2 import Picamera2, Preview
from threading import Thread
import paho.mqtt.client as mqtt
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

SECRET = "my-secret"

def sign(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)

def take_picture(picture_name, log_string):
    picam2.start_preview(Preview.QT)
    picam2.start()
    time.sleep(2)
    picam2.capture_file(picture_name)
    picam2.stop_preview()

    timestamp = datetime.datetime.now()
    with open("logs.txt", "a") as file:
        file.write(log_string + str(timestamp) + "\n")
        
def random_color():
	intcolor = randrange(3)
	if (intcolor == 0):
		return "red"
	if (intcolor == 1):
		return "yellow"
	if (intcolor == 2):
		return "green"

def make_request_weather():
    url = "http://0.0.0.0:5080/WeatherForecast"
    response = requests.get(url)
    response_json = response.json()
    #print(response_json)
    return response_json


def make_request_motioncollision():
    url = "http://0.0.0.0:5081/MotionCollisionSensor"
    response = requests.get(url)
    response_json = response.json()
    #print(response_json)
    return response_json

def motion_collision_loop(client, private_key):
    turn = 0
    while True:
        response = make_request_motioncollision()
        if response["theDetection"]["type"] == "motion":
            color = random_color()
            if color == "green":
                print("The light is green GO!")
            elif color == "yellow":
                print("The light is yellow SLOW DOWN!")
            elif color == "red":
                print("The light is red STOP!")
                if response["theDetection"]["value"] == True:
                    take_picture("traffic_publisher_photo.jpg", "Check traffic_publisher_photo.jpg for offence ")
                    print("STOP, you have violated the law!")
                    filename = './traffic_publisher_photo.jpg'
                    with open(filename, mode='rb') as file:
                        img_data = file.read()
                    enc_data = base64.b64encode(img_data).decode('utf-8')
                    response["image"] = enc_data
                    signature = sign(str.encode(json.dumps(response)), private_key)
                    message = response | {'signature': signature.hex()}
                    topic="MotionCollisionSensor"
                    result = client.publish(topic=topic, payload=json.dumps(message))
                    status = result[0]
                    if status == 0:
                        print("Message is" + json.dumps(message) + "published to topic " + topic)
                    else:
                        print("Failed to send message to topic " + topic)
        
        if response["theDetection"]["type"] == "colision" and response["theDetection"]["value"] == True:
            take_picture("traffic_publisher_photo.jpg", "Check traffic_publisher_photo.jpg for accident ")
            print("There was an accident!")
            filename = './traffic_publisher_photo.jpg'
            with open(filename, mode='rb') as file:
                img_data = file.read()
            enc_data = base64.b64encode(img_data).decode('utf-8')
            response["image"] = enc_data
                
            signature = sign(str.encode(json.dumps(response)), private_key)
            message = response | {'signature': signature.hex()}
            topic="MotionCollisionSensor"
            result = client.publish(topic=topic, payload=json.dumps(message))
            status = result[0]
            if status == 0:
                print("Message is" + json.dumps(message) + "published to topic " + topic)
            else:
                print("Failed to send message to topic " + topic)
        time.sleep(4)

def weather_loop(client, private_key):
    while True:
        response = make_request_weather()
        signature = sign(str.encode(json.dumps(response)), private_key)
        message = response | {'signature': signature.hex()}
        topic="WeatherForecast"
        result = client.publish(topic=topic, payload=json.dumps(message))
        status = result[0]
        if status == 0:
            print("Message " + json.dumps(message) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)

        time.sleep(8)

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print("connected")
        # Generate JWT token (exp 1h)
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload = {
            "sub": "client", 
            "client": f"{client._client_id.decode('utf-8')}", 
            "exp": expire_on.timestamp()
        }
        client.token = jwt.encode(payload=payload, key=SECRET, headers=headers)

    else:
        print("could not connect, return code:", return_code)
        print("publisher could not connect, return code:", return_code)
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        expire_on = datetime.datetime.utcnow()
        payload = {
            "sub": "invalid client", 
            "client": f"{client._client_id}", 
            "exp": expire_on.timestamp()
        }
        client.token = jwt.encode(payload=payload, key=SECRET, headers=headers)


if __name__ == '__main__':
    print('Program is starting...')

    broker_hostname = "localhost"
    port = 1883
    
    client1 = mqtt.Client(client_id="Client1", userdata=None)
    client2 = mqtt.Client(client_id="Client2", userdata=None)
    client1.on_connect = on_connect
    client2.on_connect = on_connect

    client1.username_pw_set(username="user1", password="password")
    client2.username_pw_set(username="user2", password="password")

    client1.connect(broker_hostname, port, 60)
    client2.connect(broker_hostname, port, 60)
    client1.loop_start()
    client2.loop_start()

    private_pem_bytes = Path("../Keys/private_key.pem").read_bytes()
    public_pem_bytes = Path("../Keys/public_key.pem").read_bytes()

    try:
        private_key_from_pem = serialization.load_pem_private_key(
            private_pem_bytes,
            password=b"my secret",
        )
        public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)
        print("Keys Correctly Loaded")
    except ValueError:
        print("Incorrect Password")

    weather_thread = Thread(target=weather_loop, args=[client1, private_key_from_pem])
    collision_thread = Thread(target=motion_collision_loop, args=[client2, private_key_from_pem])

    try:
        public_pem_data = base64.b64encode(public_pem_bytes).decode('utf-8')
        client1.publish(topic='PublicKey', payload=json.dumps({'publickey': public_pem_data}))

        print('Public Key: '+  public_pem_data)

        weather_thread.start()
        collision_thread.start()

    except KeyboardInterrupt:
        client1.loop_stop()
        client2.loop_stop()

    except Exception:
        client1.loop_stop()
        client2.loop_stop()
