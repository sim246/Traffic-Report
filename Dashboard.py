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

global weather_data, motion_data, public_key
weather_data = None
collision_data = None

broker_hostname = "localhost"
port = 1883

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("Weather")
        client.subscribe("MotionCollision")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    global weather_data, collision_data, public_key
    print("Received message: ", str(message.payload.decode("utf-8")))
    if message.topic == "WeatherForecast":
        weather_data = json.loads(str(message.payload.decode("utf-8")))
        update_thermometer(weather_data)
    elif message.topic == "MotionCollision":
        collision_data = json.loads(str(message.payload.decode("utf-8")))

def connect():
    client = mqtt.Client("Client3")
    #change this to your username and password
    client.username_pw_set(username="user1", password="password")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_hostname, port)
    client.loop_start()

    try:
        time.sleep(3)
    finally:
        client.loop_stop()

app = Dash(__name__)

if (weather_data != None):
    app.layout = html.Div([
        daq.Thermometer(
            id='my-thermometer-1',
            value=weather_data["temperature"],
            min=-40,
            max=40,
            style={
                'margin-bottom': '5%',
                'margin-left': '5%',
                'display': 'inline-block'
            }
        )
    ])
else:
    app.layout = html.Div([
        daq.Thermometer(
            id='my-thermometer-1',
            value=-40,
            min=-40,
            max=40,
            style={
                'margin-bottom': '5%',
                'margin-left': '5%',
                'display': 'inline-block'
            }
        )
    ])
value=1
@callback(
    Output('my-thermometer-1', 'value'),
    Input('interval-component', 'n_intervals')
)

def update_thermometer(value):
    if value != None:
        value = weather_data
        return (value["temperature"])

def run():
    app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    weather_thread = Thread(target=connect, args=(), daemon=False)
    weather_thread.start()

    app.run(debug=False, host='0.0.0.0')
