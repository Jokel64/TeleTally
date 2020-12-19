from __future__ import print_function

import logging
import sys
import time
import random

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from rtmidi._rtmidi import NoDevicesError
from rtmidi.midiutil import open_midiinput


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

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        global Layer_State, update_select, selected_A, selected_B
        message, deltatime = event
        self._wallclock += deltatime
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
        socketio.emit('update', all_tally_states())


# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = None

demo_mode = False
try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()
except NoDevicesError:
    demo_mode = True


if not demo_mode:
    print("Attaching MIDI input callback handler.")
    midiin.set_callback(MidiInputHandler(port_name))

    print("Entering main loop. Press Control-C to exit.")

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = "THISWILLBEOURSECRET"
app.config.from_object(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def get_state(I):
    if (I is selected_A and Layer_State is 0) or (I is selected_B and Layer_State is 1) \
            or ((I is selected_A or I is selected_B) and Layer_State is 2):
        return 'live'
    elif I is selected_A or I is selected_B:
        return 'ready'
    else:
        return 'none'


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/api/v1/tally/s/<tally_id>', methods=['GET'])
def single_tally_state(tally_id=-1):
    state = get_state(int(tally_id))
    return state

@app.route('/api/v1/tally/all')
def all_tally_states():
    state = get_state(0)[0] + get_state(1)[0] + get_state(2)[0] + get_state(3)[0]
    return state

@app.route('/dev/set/')
def set_tally():
    global selected_A, selected_B, Layer_State
    selected_A = random.choice((Input.I1, Input.I2, Input.I3, Input.I4))
    selected_B = random.choice((Input.I1, Input.I2, Input.I3, Input.I4))
    Layer_State = random.choice((State.A, State.B, State.AB))
    socketio.emit('update', all_tally_states())
    return f'A: {selected_A}, B: {selected_B}, Layer: {Layer_State}'


@socketio.on('kanal')
def handle_message(data):
    print('received message: ' + data)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
