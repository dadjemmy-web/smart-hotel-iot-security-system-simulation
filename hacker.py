import paho.mqtt.client as mqtt
import json
import time
import jwt
from mqtt_connect import create_mqtt_client

# The attacker now sends forged jwt tokens (wrong secret) to all command topics.
# Door, camera, and HVAC will reject them, and security monitor(IOT IDS) raises alerts

BROKER = "localhost"
PORT = 8883
SECRET_KEY = "my_super_secret_key_12345###EERR##0#446p"   

client = create_mqtt_client("hacker", "hacker123")
client.connect(BROKER, PORT, 60)

print(f"[{time.ctime()}] Attacker launches multiple attacks in sequence...")

# 1. Unauthorised door attempt with forged token
token = jwt.encode({"user": "attacker"}, "wrong_secret", algorithm="HS256")
client.publish("hotel/doors/entrance/request", json.dumps({"token": token, "action": "open"}))
print(" - Sent forged token for entrance door")
time.sleep(7)

# 2. Attack Reception camera1 with forged token
token = jwt.encode({"user": "attacker"}, "wrong_secret", algorithm="HS256")
client.publish("hotel/cameras/corridor5/command", json.dumps({"token": token, "command": "reboot"}))
print(" - Sent forged token for camera command")
time.sleep(7)

# 3. HVAC attack with forged token
token = jwt.encode({"user": "attacker"}, "wrong_secret", algorithm="HS256")
client.publish("hotel/room501/temperature/command", json.dumps({"token": token, "setpoint": 40}))
print(" - Attempted to set room temperature to 80°C with forged token")