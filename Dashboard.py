import requests
import json

url = "http://10.172.25.216:5080/CollisionSensor"
response = requests.get(url)
response_json = response.json()
print(response.json())


