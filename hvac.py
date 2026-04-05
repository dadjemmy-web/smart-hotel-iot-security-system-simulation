import paho.mqtt.client as mqtt
import json
import time
import jwt
from mqtt_connect import create_mqtt_client

# I added JWT verification to the HVAC command topic.
# If a command arrives with an invalid token, it will raise an alert.
# The temperature status is published every 5 seconds
# Attack attempts (setpoint > 50) trigger an alert.

BROKER = "localhost"
PORT = 8883
SECRET_KEY = "f8$kL9@mN2#pQ7zX!wE5rT4yU6iO0pA##EE5F"
SAFE_TEMP = 22
current_temp = SAFE_TEMP
ATTACK_THRESHOLD = 50

def on_connect(client, userdata, flags, rc):
    print(f"[{time.ctime()}] HVAC system connected")
    client.subscribe("hotel/room501/temperature/command")

def on_message(client, userdata, msg):
    global current_temp
    try:
        data = json.loads(msg.payload.decode())
        token = data.get("token")
        if not token:
            print(f"[{time.ctime()}] WARNING: No token in HVAC command")
            # Still raise an alert
            alert = {"alert": "ALERT!!: HVAC command received without token – blocked."}
            client.publish("hotel/security/alerts", json.dumps(alert))
            return
        # Verify JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("user")
        setpoint = data.get("setpoint")
        if setpoint is not None:
            if setpoint > ATTACK_THRESHOLD:
                alert = {"alert": f"ATTACK! Attempt to set room temp to {setpoint}°C blocked"}
                client.publish("hotel/security/alerts", json.dumps(alert))
                print(f"[{time.ctime()}] HVAC attack detected from {user}")
                current_temp = SAFE_TEMP
            else:
                current_temp = setpoint
                print(f"[{time.ctime()}] Temperature set to {setpoint}°C by {user}")
    except jwt.InvalidTokenError:
        print(f"[{time.ctime()}] WARNING: Invalid token for HVAC command")
        alert = {"alert": "ALERT!!: HVAC command with invalid token – blocked."}
        client.publish("hotel/security/alerts", json.dumps(alert))
    except Exception as e:
        print(f"[{time.ctime()}] HVAC error: {e}")

client = create_mqtt_client("hvac", "hvac123")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    status = {"temperature": current_temp, "unit": "C", "safe": current_temp <= SAFE_TEMP+2}
    client.publish("hotel/room501/temperature/status", json.dumps(status))
    print(f"[{time.ctime()}] Temp published: {current_temp}°C")
    time.sleep(5)