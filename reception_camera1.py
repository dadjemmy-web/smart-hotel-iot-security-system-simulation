import paho.mqtt.client as mqtt
import json
import time
import jwt
from mqtt_connect import create_mqtt_client

# I added JWT verification to the camera command topic.
# Only commands with a valid token will be acknowledged (and logged).


BROKER = "localhost"
PORT = 8883
SECRET_KEY = "f8$kL9@mN2#pQ7zX!wE5rT4yU6iO0pA##EE5F"

def on_connect(client, userdata, flags, rc):
    print(f"[{time.ctime()}] Corridor camera connected")
    client.subscribe("hotel/cameras/corridor5/command")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        token = data.get("token")
        if not token:
            print(f"[{time.ctime()}] WARNING: No token in camera command")
            return
        # Verify JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("user")
        # log and alert
        print(f"[{time.ctime()}] Camera command from {user}: {data.get('command')}")
    except jwt.InvalidTokenError:
        print(f"[{time.ctime()}] WARNING: Invalid token for camera command")
    except Exception as e:
        print(f"[{time.ctime()}] Camera error: {e}")

client = create_mqtt_client("camera", "cam123")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    status = {"status": "online", "monitoring": True}
    client.publish("hotel/cameras/corridor5/status", json.dumps(status))
    print(f"[{time.ctime()}] Camera status: online and monitoring")
    time.sleep(5)