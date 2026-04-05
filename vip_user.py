import paho.mqtt.client as mqtt
import json
import time
import jwt
from mqtt_connect import create_mqtt_client

# I added JWT tokens to all door requests.


BROKER = "localhost"
PORT = 8883
SECRET_KEY = "f8$kL9@mN2#pQ7zX!wE5rT4yU6iO0pA##EE5F"

client = create_mqtt_client("vip", "vip123")
client.connect(BROKER, PORT, 60)

DOOR_CYCLE = 4          
GAP_ENTRANCE_TO_LIFT = 5
GAP_LIFT_TO_ROOM = 10

print(f"[{time.ctime()}] VIP sequence started")

# ---- Lobby Access door ----
token = jwt.encode({"user": "VIP"}, SECRET_KEY, algorithm="HS256")
client.publish("hotel/doors/entrance/request", json.dumps({"token": token, "action": "open"}))
print(f"[{time.ctime()}] VIP requested entrance door")
time.sleep(DOOR_CYCLE + GAP_ENTRANCE_TO_LIFT)

# ---- Lift ----
token = jwt.encode({"user": "VIP"}, SECRET_KEY, algorithm="HS256")
client.publish("hotel/doors/lift/request", json.dumps({"token": token, "action": "open"}))
print(f"[{time.ctime()}] VIP requested lift")
time.sleep(DOOR_CYCLE + GAP_LIFT_TO_ROOM)

# ---- Room 501 ----
token = jwt.encode({"user": "VIP"}, SECRET_KEY, algorithm="HS256")
client.publish("hotel/doors/room501/request", json.dumps({"token": token, "action": "open"}))
print(f"[{time.ctime()}] VIP requested room 501")

print(f"[{time.ctime()}] VIP sequence complete")