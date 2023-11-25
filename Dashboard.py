import base64
import json
import time
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
from threading import Thread
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from TrafficPublisher.publisher import start

global weather_data, motion_collision_data, public_key

public_key = "NA"
weather_data = "NA"
motion_collision_data = "NA"

broker_hostname = "localhost"
port = 1883

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("Weather")
        client.subscribe("MotionCollision")
        client.subscribe("PublicKey")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    global weather_data, motion_collision_data, public_key
    print("Received message: ", str(message.payload.decode("utf-8")))
    if message.topic == "WeatherForecast":
        weather_data = json.loads(str(message.payload.decode("utf-8")))
    elif message.topic == "MotionCollision":
        motion_collision_data = json.loads(str(message.payload.decode("utf-8")))
    elif message.topic == "PublicKey":
        public_key_data = json.loads(message.payload.decode("utf-8"))
        public_key_bytes = base64.b64decode(public_key_data.get('publickey'))
        public_key = serialization.load_pem_public_key(public_key_bytes)

def connect():
    client = mqtt.Client("Client3")
    client.username_pw_set(username="user3", password="password")
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
    if weather_data != "NA":
        return weather_data
        
def get_public_key():
    global public_key
    if public_key != "NA":
        return public_key

def get_motion_collision():
    global motion_collision_data
    if motion_collision_data != "NA":
        return motion_collision_data

public_key = get_public_key()
weather_data = get_weather()
motion_collision_data = get_motion_collision()





app = Dash(__name__)

try:
    app.layout = html.Div([
        daq.Thermometer(
            id='my-thermometer-1',
            value=weather_data["temperature"],
            label=weather_data["date"] + " " + weather_data["postalCode"] + " " + weather_data["type"] + " " + weather_data["intensity"],
            min=-40,
            max=40,
            style={
                'margin-bottom': '5%',
                'margin-left': '5%',
                'display': 'inline-block'
            }
        ),
        html.Div([], id="collision-display"),
        html.Img(id='collision-img'),
        dcc.Interval(
            id='interval-component',
            interval=3000,  # in milliseconds
            n_intervals=0
        ),
    ])
except TypeError:
    app.layout = html.Div([
        daq.Thermometer(
            id='my-thermometer-1',
            value=-40,
            label="Loading Data ...",
            min=-40,
            max=40,
            style={
                'margin-bottom': '5%',
                'margin-left': '5%',
                'display': 'inline-block'
            }
        ),
        html.Div([], id="collision-display"),
        html.Img(id='collision-img'),
        dcc.Interval(
            id='interval-component',
            interval=3000,  # in milliseconds
            n_intervals=0
        ),
    ])

@callback(
    Output('my-thermometer-1', 'value'),
    Output('my-thermometer-1', 'label'),
    Input('interval-component', 'n_intervals')
)

def update_thermometer(value):
    global weather_data, public_key
    
    weather_data = get_weather()
    public_key = get_public_key()
    
    if weather_data != None and public_key != None:
        if verify(bytes.fromhex(weather_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(weather_data, ['signature']))),
                                           public_key):
            lable = weather_data["date"] + " " + weather_data["postalCode"] + " " + weather_data["type"] + " " + weather_data["intensity"]
            return (weather_data["temperature"], lable)

@callback(
    Output('collision-display', 'children'),
    Input('interval-component', 'n_intervals')
)

def update_collision(value):
    global motion_collision_data
    motion_collision_data = get_motion_collision()
    public_key = get_public_key()
    if motion_collision_data != None and public_key != None:
        if verify(bytes.fromhex(motion_collision_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(motion_collision_data, ['signature']))),
                                           public_key):
            return (
                    f"Date: {motion_collision_data.get('date')}, " +
                    f"Postal Code: {motion_collision_data.get('postalCode')}, " +
                    f"Detection Type: {motion_collision_data.get('detection').get('type')}, " +
                    f"Collision Value: {motion_collision_data.get('detection').get('value')}"
            )

@callback(
    Output('collision-img', 'src'),
    Input('interval-component', 'n_intervals')
)

def update_collision_image(value):
    if public_key != None and motion_collision_data != None:
        if isinstance(motion_collision_data.get("image"), str):
            if verify(bytes.fromhex(motion_collision_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(motion_collision_data, ['signature']))),
                                           public_key):
                return 'data:image/jpg;base64,' + motion_collision_data.get("image")

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

if __name__ == '__main__':
    
    conn = Thread(target=start, args=())
    conn.start()
    
    client = mqtt.Client("Client3")
    client.username_pw_set(username="user3", password="password")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_hostname, port)
    client.loop_start()
    
    app.run(host='0.0.0.0', port=5000)

