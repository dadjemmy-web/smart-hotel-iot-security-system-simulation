import paho.mqtt.client as mqtt
import json
import threading
import time
import jwt
from mqtt_connect import create_mqtt_client

# I wanted a realistic card‑reader sequence even for denied attempts.

BROKER = "localhost"
PORT = 8883
SECRET_KEY = "f8$kL9@mN2#pQ7zX!wE5rT4yU6iO0pA##EE5F"
ALLOWED_USERS = ["VIP"]

def on_connect(client, userdata, flags, rc):
    print(f"[{time.ctime()}] Door controller connected")
    client.subscribe("hotel/doors/+/request")

def publish_display(door, text):
    payload = json.dumps({"display": text})
    client.publish(f"hotel/doors/{door}/command", payload)
    print(f"[{time.ctime()}] Published to {door}: {text}")

def door_sequence(door, user):
    # Step 1: card reading
    publish_display(door, "requesting access by authorized user")
    time.sleep(1)
    # Step 2: grant access
    if door == "lift":
        publish_display(door, "access granted- LIFT DOOR OPENS")
    else:
        publish_display(door, "access granted- DOOR UNLOCKED")
    time.sleep(3)
    # Step 3: close / lock
    if door == "lift":
        publish_display(door, "LIFT DOOR CLOSES")
    else:
        publish_display(door, "DOOR LOCKED")

def denied_sequence(door):
    # Simulate card read attempt by unknown user
    publish_display(door, "requesting access by unknown user")
    time.sleep(1)
    publish_display(door, "Access denied - LOCKED")

def on_message(client, userdata, msg):
    door = msg.topic.split('/')[2]
    try:
        data = json.loads(msg.payload.decode())
        token = data.get("token")
        if not token:
            # No token – treat as unknown user
            threading.Thread(target=denied_sequence, args=(door,)).start()
            return
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("user")
        action = data.get("action")
        if user in ALLOWED_USERS and action == "open":
            threading.Thread(target=door_sequence, args=(door, user)).start()
        else:
            threading.Thread(target=denied_sequence, args=(door,)).start()
    except jwt.InvalidTokenError:
        print(f"[{time.ctime()}] Invalid token on {door}")
        threading.Thread(target=denied_sequence, args=(door,)).start()
    except Exception as e:
        print(f"[{time.ctime()}] Error: {e}")

client = create_mqtt_client("door_controller", "door123")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()