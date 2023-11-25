import base64
import json
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
from threading import Thread
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

global weather_data, motion_data, public_key
weather_data = "Loading Weather Data..."
collision_data = "Loading Collision Data..."

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
    global weather_data, collision_data, public_key
    print("Received message: ", str(message.payload.decode("utf-8")))
    if message.topic == "WeatherForecast":
        weather_data = json.loads(str(message.payload.decode("utf-8")))
    elif message.topic == "MotionCollision":
        collision_data = json.loads(str(message.payload.decode("utf-8")))
    elif message.topic == "PublicKey":
        public_key_data = json.loads(message.payload.decode("utf-8"))
        public_key_bytes = base64.b64decode(public_key_data.get('publickey'))
        public_key = serialization.load_pem_public_key(public_key_bytes)

def connect():
    client = mqtt.Client("Client3")
    #change this to your username and password
    client.username_pw_set(username="user_name", password="password")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_hostname, port)
    client.loop_start()

    try:
        time.sleep(9999999)
    finally:
        client.loop_stop()

app = Dash(__name__)

app.layout = html.Div([
    daq.Thermometer(
        id='my-thermometer-1',
        value=5,
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
    global public_key
    if weather_data == "Loading Weather Data...":
        return
    elif public_key is not None and verify(bytes.fromhex(weather_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(weather_data, ['signature']))),
                                           public_key):
        return weather_data.get('temperatureC'), weather_data.get('summary')
    return '38', "bad sign"

@callback(
    Output('collision-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_collision(value):
    global public_key
    if collision_data == "Loading Collision Data...":
        return
    elif public_key is not None and verify(bytes.fromhex(collision_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(collision_data, ['signature']))),
                                           public_key):
        return (
                f"Date: {collision_data.get('date')}, " +
                f"Postal Code: {collision_data.get('postalCode')}, " +
                f"Detection Type: {collision_data.get('detection').get('type')}, " +
                f"Collision Value: {collision_data.get('detection').get('value')}"
        )
    return

@callback(
    Output('collision-img', 'src'),
    Input('interval-component', 'n_intervals')
)
def update_collision_image(value):
    if collision_data == "Loading Collision Data...":
        return

    if isinstance(collision_data.get("image"), str):
        if public_key is not None and verify(bytes.fromhex(collision_data.get('signature')),
                                           str.encode(json.dumps(excludeKeysFromDict(collision_data, ['signature']))),
                                           public_key):
            return 'data:image/jpg;base64,' + collision_data.get("image")

    return

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
    weather_thread = Thread(target=connect, args=(), daemon=False)
    weather_thread.start()

    # Start the MQTT publisher
    from publisher import publish_weather_and_collision
    publish_thread = Thread(target=publish_weather_and_collision, args=(), daemon=False)
    publish_thread.start()

    app.run(debug=False, host='0.0.0.0')

