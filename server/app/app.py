#!/usr/bin/env python
__author__ = "Jakob Englert"
__copyright__ = "Copyright 2020, EMT Event-Media-Tec GmbH"

import json
import logging
import os
import random
import sys
import threading
import time

import paho.mqtt.client as mqtt
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from rtmidi._rtmidi import NoDevicesError
from rtmidi.midiutil import open_midiinput

######################################################  GLOBAL  #######################################################
broker = '127.0.0.1'
mqtt_port = 1883
topic = "/update"
client_id = 'midi_server'
client = None

message_counter = 0

settings = {
    'esp_update_period': 5
}

if os.path.isfile('settings.json'):
    settings.update(json.load(open("settings.json")))

tally_MQTT_clients = {
    1: {
        'first_connect': 0.0,
        'alive_packages': 0,
        'alive_timeouts': 0,
        'last_alive': 0.0,
        'connected': False
    },
    2: {
        'first_connect': 0.0,
        'alive_packages': 0,
        'alive_timeouts': 0,
        'last_alive': 0.0,
        'connected': False
    },
    3: {
        'first_connect': 0.0,
        'alive_packages': 0,
        'alive_timeouts': 0,
        'last_alive': 0.0,
        'connected': False
    },
    4: {
        'first_connect': 0.0,
        'alive_packages': 0,
        'alive_timeouts': 0,
        'last_alive': 0.0,
        'connected': False
    },
}

# Loggers
log_mqtt = logging.getLogger("MQTT")
log_api = logging.getLogger("API")
log_midi = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)


#######################################################  MIDI  ########################################################
class State:
    A, B, AB = range(3)


class Input:
    I1, I2, I3, I4 = range(4)


class Layer:
    A, B = range(2)


Layer_State = State.A
selected_A = Input.I1
selected_B = Input.I2
update_select = Layer.A


def get_state(I):
    if (I is selected_A and Layer_State is 0) or (I is selected_B and Layer_State is 1) \
            or ((I is selected_A or I is selected_B) and Layer_State is 2):
        return 'live'
    elif I is selected_A or I is selected_B:
        return 'ready'
    else:
        return 'none'


def all_tally_states():
    state = get_state(0)[0] + get_state(1)[0] + get_state(2)[0] + get_state(3)[0]
    return state


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        global Layer_State, update_select, selected_A, selected_B
        message, deltatime = event
        self._wallclock += deltatime
        selected_B_save = selected_B
        selected_A_save = selected_A
        Layer_State_save = Layer_State

        if message[0] is 176 and message[1] is 17:
            if message[2] is 0:
                Layer_State = State.A
            elif message[2] is 127:
                Layer_State = State.B
            else:
                Layer_State = State.AB
        if message[0] is 176 and message[1] is 0:
            update_select = message[2]

        if message[0] is 192:
            if update_select is Layer.A:
                selected_A = message[1]
            elif update_select is Layer.B:
                selected_B = message[1]

        if selected_A_save != selected_A or selected_B_save != selected_B or Layer_State_save != Layer_State:
            states = all_tally_states()
            socketIO.emit('update', states)
            publish(states)


port = None

demo_mode = False
try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()
except NoDevicesError:
    demo_mode = True

if not demo_mode:
    log_midi.info("Attaching MIDI input callback handler.")
    midiin.set_callback(MidiInputHandler(port_name))


#######################################################  MQTT  ########################################################
def on_connect(client_instance, userdata, flags, rc):
    global client
    if rc == 0:
        log_mqtt.info("Connected to MQTT Broker!")
        client.subscribe("/feedback/alive")
        client.subscribe("/feedback/connected")
    else:
        log_mqtt.error("Failed to connect, return code %d\n", rc)


def on_message(client_instance, userdata, msg):
    no = int(msg.payload)
    msgtopic = str(msg.topic).replace(' ', '')

    if tally_MQTT_clients[no]['first_connect'] == 0.0:
        tally_MQTT_clients[no]['first_connect'] = time.time()
        tally_MQTT_clients[no]['connected'] = True

    if msgtopic == "/feedback/alive":
        tally_MQTT_clients[no]['alive_packages'] += 1
        tally_MQTT_clients[no]['last_alive'] = time.time()
        tally_MQTT_clients[no]['connected'] = True
        log_mqtt.info(f"Tally Light {no} alive.")

    elif msgtopic == "/feedback/connected":
        log_mqtt.info(f"Tally Light {no} connected.")
    else:
        log_mqtt.error(f"Topic {msgtopic} is unknown and will be ignored.", )


def connect_mqtt():
    global client
    # Set Connecting Client ID
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, mqtt_port)
    return client


def publish(msg, broadcast=False):
    global message_counter
    top = "/broadcast" if broadcast else topic
    result = client.publish(top, msg)

    # result: [0, 1]
    status = result[0]
    if status == 0:
        if not broadcast:
            log_mqtt.info(f"Sent `{msg}` to topic `{top}` [{message_counter}]")
            message_counter += 1
    else:
        log_mqtt.error(f"Failed to send message to topic {top}")
        client.disconnect()
        while not client.is_connected():
            # noinspection PyBroadException
            try:
                log_mqtt.info("Reconnecting...")
                client.reconnect()
            except Exception as e:
                log_mqtt.error("Cant reach MQTT-Server! Trying again in 5 sec.")
            time.sleep(5)
        publish(msg)


client = connect_mqtt()


def broadcast():
    while True:
        publish(all_tally_states(), broadcast=True)
        esp_state_emit()
        time.sleep(3)


def alive_checker():
    while True:
        for idx in tally_MQTT_clients:
            elm = tally_MQTT_clients[idx]
            if elm['first_connect'] != 0 and elm['alive_packages'] != 0:
                if time.time() - elm['last_alive'] - 0.5 * settings['esp_update_period'] > settings[
                    'esp_update_period']:
                    log_mqtt.info("timeout")
                    elm['connected'] = False
                    elm['alive_timeouts'] += 1
                    elm['last_alive'] = time.time()
                    esp_state_emit()
        time.sleep(1)


client.loop_start()
broadcast_service = threading.Thread(target=broadcast)
alive_service = threading.Thread(target=alive_checker)


########################################################  API  #########################################################
app = Flask(__name__)
app.config['TESTING'] = False
app.config['SECRET_KEY'] = "m238fn3o10enmd4i23iod129jdk39r5j"
app.config.from_object(__name__)
socketIO = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/api/v1/tally/s/<tally_id>', methods=['GET'])
def single_tally_state(tally_id=-1):
    state = get_state(int(tally_id))
    return state


@app.route('/api/v1/tally/all')
def all_tally_states_api():
    state = all_tally_states()
    return state


@app.route('/dev/set/')
def set_tally():
    global selected_A, selected_B, Layer_State
    selected_A = random.choice((Input.I1, Input.I2, Input.I3, Input.I4))
    selected_B = random.choice((Input.I1, Input.I2, Input.I3, Input.I4))
    Layer_State = random.choice((State.A, State.B, State.AB))
    states = all_tally_states()
    socketIO.emit('update', states)
    publish(states)
    return f'A: {selected_A}, B: {selected_B}, Layer: {Layer_State}'


@socketIO.on('apirequest')
def handle_message(data):
    if data == "espstate":
        esp_state_emit()
    elif data == "update":
        socketIO.emit('update', all_tally_states())


def esp_state_emit():
    rl = []
    for idx in tally_MQTT_clients:
        elm = tally_MQTT_clients[idx]
        js = {
            'Name': f"Tally Light {idx}",
            'Connected': elm['connected'],
            'alive_packages': elm['alive_packages'],
            'alive_timeouts': elm['alive_timeouts'],
            'last_alive': f"{round(time.time() - elm['last_alive'])} seconds ago." if elm['last_alive'] != 0.0 else "-",
        }
        rl.append(json.dumps(js))
    socketIO.emit('espstate', rl)


broadcast_service.start()
alive_service.start()

if __name__ == '__main__':
    socketIO.run(app, host='0.0.0.0', port=5000)
