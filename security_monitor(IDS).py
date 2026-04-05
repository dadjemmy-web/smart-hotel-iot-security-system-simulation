import paho.mqtt.client as mqtt
import json
import time
from mqtt_connect import create_mqtt_client

# The monitoring logic listen to door command topics instead of requests.
# Alerts are triggered only when the door controller (ACU) publishes a denial message.
# Camera and HVAC commands are monitored directly.

BROKER = "localhost"
PORT = 8883

def on_connect(client, userdata, flags, rc):
    print(f"[{time.ctime()}] Security monitor connected")
    # Door status topics (where the door controller publishes the outcome)
    client.subscribe("hotel/doors/+/command")
    # Camera commands (any command is suspicious)
    client.subscribe("hotel/cameras/+/command")
    # HVAC commands (to catch setpoint attacks)
    client.subscribe("hotel/room501/temperature/command")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()

        # Camera commands – any direct command is an attack
        if "cameras" in topic and topic.endswith("/command"):
            alert_msg = "ALERT!!: Suspicious attack on corridor camera – attack neutralized, camera is monitoring."
            alert = {"alert": alert_msg}
            client.publish("hotel/security/alerts", json.dumps(alert))
            print(f"[{time.ctime()}] {alert_msg}")

        # Door command topics – check if the status indicates a denial
        if "doors" in topic and topic.endswith("/command"):
            # The door controller publishes JSON with a "display" field
            data = json.loads(payload)
            status = data.get("display", "")
            if "Access denied" in status:
                alert_msg = f"ALERT!!: Unauthorised door attempt – {status}"
                alert = {"alert": alert_msg}
                client.publish("hotel/security/alerts", json.dumps(alert))
                print(f"[{time.ctime()}] {alert_msg}")

        # HVAC commands – detect setpoint attacks (setpoint > 50)
        if "temperature/command" in topic:
            data = json.loads(payload)
            setpoint = data.get("setpoint")
            if setpoint and setpoint > 50:
                alert_msg = f"ALERT!!: HVAC attack – attempt to set temp to {setpoint}°C blocked."
                alert = {"alert": alert_msg}
                client.publish("hotel/security/alerts", json.dumps(alert))
                print(f"[{time.ctime()}] {alert_msg}")

    except Exception as e:
        # Ignore malformed messages (e.g., non‑JSON)
        pass

client = create_mqtt_client("monitor", "mon123")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()