"""
On request (SIGINT), posts the current temperature information from Cube
to the web server.
If upload fails (e.g. internet connection is down),
retains the data until the next upload request.
"""

################################################################################
# Collecting information from Cube
################################################################################

from elvmax import cube, house, messages, devices

connection = None
the_house = house.House()

# print 'Searching Cube'
# cubes = cube.Search.list_cubes()
# if len(cubes) != 1:
#     raise ValueError('Expected to find 1 Cube in the network')
#
# found_cube = cubes[0]
# print 'Found cube ' + found_cube[0]
#
# connection = cube.Connection()
# connection.host = found_cube[1]
# connection.port = found_cube[2]


################################################################################
# Custom JSON encoder: strings are b16-encoded (hex)
################################################################################

import json
import base64


class Base16Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return base64.b16encode(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

################################################################################
# Uploading
################################################################################

import httplib
import signal
import time


stat = {}

def encode_data(data):
    """
    Produces JSON (custom encoder just does not work)
    """
    return '{\n' + ',\n'.join('"' + '%016x' % key + '": "' + base64.b16encode(data[key]) + '"' for key in data) + '\n}'

def encode_temperature(t):
    """
    convert to 2-byte fixed-point I.F string
    """
    if not t:
        return '\xFF\xFF'
    rounded = float(int((t) * 2)) / 2.0
    integer = int(rounded)
    return str(chr(integer & 0xFF)) + str(chr(int((t - integer) * 256.0) & 0xFF))

def upload():
    global stat
    print 'Requested to upload data'
    print ','.join(str(the_house.rf_address_to_device[key].temperature())
        for key in the_house.rf_address_to_device)

    data = ''.join(encode_temperature(the_house.rf_address_to_device[key].temperature())
                   for key in the_house.rf_address_to_device)
    stat[int(round(time.time() * 1000))] = data
    headers = {"Content-type": "text/plain"}
    conn = None
    try:
        conn = httplib.HTTPConnection("vector-space.appspot.com")
        conn.request("POST", "/temperature_statistics", encode_data(stat), headers)
        stat = {}
        print 'Data uploaded'

    except httplib.HTTPException, e:
        print e
    finally:
        conn and conn.close()


def connect_and_upload():
    connection = cube.Connection()
    connection.host = '192.168.3.246'
    connection.port = 62910
    connection.on_message = the_house.on_message
    connection.start()
    time.sleep(5.0)
    upload()
    connection.stop()

signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGINT, lambda signum, frame: connect_and_upload())


################################################################################
# Requesting the Cube to toggle all thermostats into VACATION mode
# till the end of current half-hour on signal USR1 (Linux only)
################################################################################

import platform
import datetime

def toggle_vacation_mode():
    connection = cube.Connection()
    connection.host = '192.168.3.246'
    connection.port = 62910
    connection.on_message = the_house.on_message
    connection.start()
    time.sleep(5.0)

    # round up to next half-hour
    until = datetime.datetime.fromtimestamp(((int(time.time()) + 1800)/1800)*1800)

    for rf_address in the_house.rf_address_to_device:
        device = the_house.rf_address_to_device[rf_address]
        room_id = device.metadata.room_id
        t = device.target_temperature()

        print "Setting t=%d, mode=VACATION, until=%s in room %d" % (t, until, room_id)
        cmd = messages.command_set_temperature(
            rf_address,
            room_id,
            devices.Device.Mode.VACATION,
            t,
            until.year, until.month, until.day, until.hour*2 + (1 if until.minute > 0 else 0)
        )
        connection.write_message(cmd)

    connection.stop()

if platform.system() != 'Windows':
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, lambda signum, frame: toggle_vacation_mode())

################################################################################
# Requesting the Cube to send updated data on signal USR2 (Linux only)
################################################################################

if platform.system() != 'Windows':
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, lambda signum, frame: connection.write_message(messages.command(messages.request_types.GET_DEVICE_LIST)))


################################################################################
# Wait for shutdown signal
################################################################################

import threading
shutdown_event = threading.Event()


def shutdown():
    shutdown_event.set()

signal.signal(signal.SIGTERM, lambda signum, frame: shutdown())

while 1:
    try:
        shutdown_event.wait(0.1)
        if shutdown_event.is_set():
            break
    except:
        pass
