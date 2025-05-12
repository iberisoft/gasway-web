from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
from config import MQTT_CONFIG

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to store sensor data
sensors_data = {}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("gasway/#")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        sensor_name = topic.split('/')[-1]
        payload = json.loads(msg.payload.decode())
        
        if 'value' in payload and 'unit' in payload:
            sensors_data[sensor_name] = {
                'value': round(float(payload['value']), 4),
                'unit': payload['unit']
            }
            socketio.emit('sensor_update', {
                'sensor': sensor_name,
                'data': sensors_data[sensor_name]
            })
    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT client setup
mqtt_client = mqtt.Client()
if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
    mqtt_client.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'])
mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html', sensors=sensors_data)

if __name__ == '__main__':
    socketio.run(app, debug=True) 