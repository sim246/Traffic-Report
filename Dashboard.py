import base64
import json
import time
from queue import Queue 
from dash import Dash, html, dcc, Input, Output, callback
import paho.mqtt.client as mqtt
import dash_daq as daq
from threading import Thread

global weather_data

weather_data = ""
collision_data = None
broker_hostname = "localhost"
port = 1883



def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("WeatherForecast")
        client.subscribe("MotionCollisionSensor")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
	global weather_data 
	print("Received message: ", str(message.payload.decode("utf-8")))
	if message.topic == "WeatherForecast":
		weather_data = json.loads(str(message.payload.decode("utf-8")))
	elif message.topic == "MotionCollision":
		collision_data = json.loads(str(message.payload.decode("utf-8")))

def connect():
    client = mqtt.Client("Client3")
    client.username_pw_set(username="user1", password="password")
    client.on_connect = on_connect	
    client.on_message = on_message
    client.connect(broker_hostname, port)
    client.loop_forever()



app = Dash(__name__)

if (weather_data != ""):
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
value=""
@callback(
    Output('my-thermometer-1', 'value'),
    Input('interval-component', 'n_intervals')
)

def update_thermometer(value):
    global weather_data
    if weather_data != "":
        value = weather_data
        return (value["temperature"])

def run_app():
    app.run(debug=False, host='0.0.0.0')
     
     
        
if __name__ == '__main__':
	conn = Thread(target=connect, args =(), daemon=False)
	run = Thread(target=run_app, args =(), daemon=False)
	
	conn.start()
	run.start()
