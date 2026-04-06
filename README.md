# smart-hotel-iot-security-system-simulation

A Python-based IoT security simulation demonstrating defence in depth across door access control, camera command channels, and HVAC systems,using MQTT with TLS encryption and JWT authentication at device controller level.

Three security-critical components, door access control, cameras, and HVAC are each simulated as Python scripts communicating over a real MQTT broker. 
Rather than trusting the MQTT broker as the main security boundary, every controller (ACU) enforces JWT authentication at device level, blocking unauthorised commands even from attackers with valid broker credentials. A lightweight IoT IDS monitors all channels simultaneously, publishing real-time alerts to a Node-RED dashboard, providing live visual visibility of every device status, access event, and security alert in one place. This ensures attacks are not just blocked but detected, alerted, and visible in real time. Together, these layers address a gap most commercial IoT deployments leave entirely unguarded.

## Components
- `door_controller(ACU).py` — Door access control unit with JWT verification
- `reception_camera1.py` — Camera command handler with JWT verification
- `hvac.py` — HVAC controller with JWT verification and setpoint protection
- `security_monitor(IDS).py` — Lightweight IoT IDS that monitors all MQTT topics across device channels and publishes real-time alerts
- `hacker.py` — JWT Injection Attack Simulator. post-breach adversary injecting forged tokens across door, camera, and HVAC channels
- `mqtt_connect.py` — Shared MQTT connection utility with TLS configuration

## Security Architecture
- TLS encryption on MQTT broker (port 8883)
- JWT verification at each device controller independently — no central authority
- Real-time intrusion detection and alerting via lightweight IoT IDS

## Simulation Flow

```
          Card tap → JWT created
                    ↓
                TLS Tunnel
                    ↓
  Mosquitto Broker — authenticates device
                    ↓
Door Controller(ACU) — verifies JWT → decision made
                    ↓
     Result published back to Broker
                    ↓
       ┌────────────────────────┐
       ↓                        ↓
Security Monitor (IDS)       Node-RED
checks for denials            picks up status
or attacks                        ↓
       ↓                    Sends to Dashboard
  If attack →                     ↓
  publish alert             Security team
  to broker                  sees status
       ↓
  Node-RED picks
  up the alert
       ↓
  Dashboard shows
  alert
```
## Important — Connections & Environment

This project requires three background services running simultaneously 
before any Python script will work:

- **Mosquitto MQTT Broker** — must be running on port 8883 with TLS certificates 
  and a configured password file. Without this, no script can connect.

- **Node-RED** — must be running with the project flow imported and the MQTT 
  broker configured with TLS and correct credentials. The dashboard will not 
  display anything without this.

- **Python Environment** — requires `paho-mqtt`, `pyjwt`, and `cryptography` 
  installed. Scripts will fail to import without these.

> You cannot clone this repository and run the scripts directly. 
> The broker, certificates, MQTT users, and Node-RED flow must all 
> be configured first.

## Note
Attackers can compromise smart building IoT systems through various means including credential brute-force, replay attacks, Man-in-the-Middle 
interception, firmware extraction and many more. This simulation specifically focuses only on **forged JWT token injection** across doors, cameras, and HVAC channels targeting the device authentication layer after broker access is assumed compromised.

## Simulation Video Here:
