from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json

global weather_data, motion_collision_data, public_key
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
        #client.subscribe("PublicKey")
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

def get_weather():
    global weather_data
    if weather_data != "":
        return weather_data

def get_motion_collision():
    global motion_collision_data
    if motion_collision_data != "":
        return motion_collision_data

@app.route('/')
def hello_world():
    weather_data = get_weather()
    motion_collision_data = get_motion_collision()
    if motion_collision_data != "":
        return render_template('index.html', motion_collision = motion_collision_data, weather = weather_data)

if __name__ == '__main__':
    client = mqtt.Client()
    client.username_pw_set("user1", "password")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost')
    client.loop_start()

    app.run(host='0.0.0.0', port=port)
