import base64
import requests
import json
import time
from threading import Thread
import paho.mqtt.client as mqtt
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

###### Signing messages
def sign(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def take_picture(picam2, picture_name, log_string):
    picam2.capture_file(picture_name)

    # Saves the current datetime to a file
    timestamp = datetime.datetime.now()

    with open("logs.txt", "a") as file:
        file.write(log_string + str(timestamp) + "\n")

def motion_collision_loop(picam2, client, private_key):
    turn = 0
    while True:
        if turn == 0:
            turn += 1
            print("The light is green GO!")
        elif turn == 1:
            turn += 1
            print("The light is yellow SLOW DOWN!")
        elif turn == 2:
            turn = 0
            print("The light is red STOP!")

            res = requests.get('http://localhost:5081/MotionCollision')
            response = json.loads(res.text)

            if response["detection"]["value"] == True:
                thread = Thread(target=take_picture,
                                args=(picam2, "traffic_publisher_photo.jpg", "Check traffic_publisher_photo.jpg for offence ",))
                thread.start()
                thread.join()

                print("You violated the law")

                filename = './traffic_publisher_photo.jpg'
                with open(filename, mode='rb') as file:
                    img_data = file.read()
                enc_data = base64.b64encode(img_data).decode('utf-8')
                print(enc_data)

                response["image"] = enc_data

            signature = sign(str.encode(json.dumps(response)), private_key)
            message = response | {'signature': signature.hex()}
            print(message)
            result = client.publish(topic='MotionCollision', payload=json.dumps(message))
            status = result[0]
            if status == 0:
                print("Message "+ json.dumps(message) + " is published to topic MotionCollision")
            else:
                print("Failed to send message to topic MotionCollision")

        time.sleep(1.5)

def weather_loop(client, private_key):
    while True:
        res = requests.get('http://localhost:5080/WeatherForecast')
        response = json.loads(res.text)

        signature = sign(str.encode(json.dumps(response[0])), private_key)
        message = response[0] | {'signature': signature.hex()}

        print(message)
        result = client.publish(topic='Weather', payload=json.dumps(message))
        status = result[0]
        if status == 0:
            print("Message "+ json.dumps(message) + " is published to topic Weather")
        else:
            print("Failed to send message to topic Weather")

        time.sleep(2)

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print(f"${client} connected")
    else:
        print("publisher could not connect, return code:", return_code)

if __name__ == '__main__':
    print('Program is starting...')

    broker_hostname = "localhost"
    port = 1883
    
    client1 = mqtt.Client(client_id="Client1", userdata=None)
    client2 = mqtt.Client(client_id="Client2", userdata=None)
    client1.on_connect = on_connect
    client2.on_connect = on_connect

    # change with your user and password auth
    client1.username_pw_set(username="u1", password="p1")
    client2.username_pw_set(username="u2", password="p2")

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

    picam2 = make_camera()
    weather_thread = Thread(target=weather_loop, args=[client1, private_key_from_pem])
    collision_thread = Thread(target=motion_collision_loop, args=[picam2, client2, private_key_from_pem])

    try:
        public_pem_data = base64.b64encode(public_pem_bytes).decode('utf-8')
        client1.publish(topic='PublicKey', payload=json.dumps({'publickey': public_pem_data}))

        print('Public Key: '+  public_pem_data)

        weather_thread.start()
        collision_thread.start()

    except KeyboardInterrupt:
        picam2.stop()
        client1.loop_stop()
        client2.loop_stop()

    except Exception:
        picam2.stop()
        client1.loop_stop()
        client2.loop_stop()