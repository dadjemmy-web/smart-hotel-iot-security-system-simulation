
# This sets up TLS with my self‑signed CA and uses username/password.

import paho.mqtt.client as mqtt
import ssl

def create_mqtt_client(username, password):
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set(ca_certs="C:/Program Files/mosquitto/certs/ca.crt",
                   certfile=None, keyfile=None,
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLS)
    return client