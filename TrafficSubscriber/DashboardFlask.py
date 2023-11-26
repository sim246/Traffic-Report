from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json
import base64
import shutil
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

global weather_data, motion_collision_data, public_key

public_key = ""
weather_data = ""
motion_collision_data = ""

app = Flask(__name__)

topic1 = 'WeatherForecast'
topic2 = 'MotionCollisionSensor'
port = 5000
    
def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("WeatherForecast")
        client.subscribe("MotionCollisionSensor")
        client.subscribe("PublicKey")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    global weather_data, motion_collision_data, public_key
    print("Received message: ")
    if message.topic == topic1:
        weather_data = json.loads(str(message.payload.decode("utf-8")))
        print(weather_data)
    elif message.topic == topic2:
        motion_collision_data = json.loads(str(message.payload.decode("utf-8")))
        print(motion_collision_data["date"] + motion_collision_data["postalCode"] + str(motion_collision_data["theDetection"]))
    elif message.topic == "PublicKey":
        public_key_data = json.loads(message.payload.decode("utf-8"))
        public_key_bytes = base64.b64decode(public_key_data.get('publickey'))
        public_key = serialization.load_pem_public_key(public_key_bytes)

def get_weather():
    global weather_data
    if weather_data != "":
        return weather_data

def get_motion_collision():
    global motion_collision_data
    if motion_collision_data != "":
        return motion_collision_data

def get_public_key():
    global public_key
    if public_key != "":
        return public_key

###### Verifying signature
def verify(signature, message, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def excludeKeysFromDict(dictObj, keysArray):
    return {x: dictObj[x] for x in dictObj if x not in keysArray}

@app.route('/')
def start():
    public_key = get_public_key()
    weather_data = get_weather()
    motion_collision_data = get_motion_collision()
    if public_key != None:
        if weather_data != None:
            if verify(bytes.fromhex(weather_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(weather_data, ['signature']))),
                                           public_key):
                if motion_collision_data != None:
                    if verify(bytes.fromhex(motion_collision_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(motion_collision_data, ['signature']))),
                                           public_key):
                        src_dir = "./../TrafficPublisher"
                        dst_dir = "./static"
                        jpgfile = os.path.join(src_dir, "traffic_publisher_photo.jpg")
                        shutil.copy(jpgfile, dst_dir)
                        return render_template('index.html', weather = weather_data, motion_collision = motion_collision_data)
                else:
                    return render_template('index.html', weather = weather_data)
    else:
        return render_template('wait.html')

if __name__ == '__main__':
    client = mqtt.Client()
    client.username_pw_set("user1", "password")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost')
    client.loop_start()

    app.run(host='0.0.0.0', port=port)
