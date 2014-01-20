import messages
import devices


class House(object):
    """
    House contains maps of rooms and devices.
    Their state and configuration is populated from incoming Cube messages.
    """
    rf_address_to_device = {}
    room_id_to_room = {}

    def on_message(self, message):
        print message
        if messages.response_types.has_key(chr(message[0])):
            message_object = messages.response_types[chr(message[0])](str(message[2:]))
            self.handlers[message_object.__class__](self, message_object)
        else:
            print "No handler for message: " + chr(message[0])

    def handle_metadata_message(self, message):
        for device_metadata in message.devices_metadata:
            if self.rf_address_to_device.has_key(device_metadata.rf_address):
                device = self.rf_address_to_device[device_metadata.rf_address]
            else:
                device = self.device_types[device_metadata.device_type]()
                self.rf_address_to_device[device_metadata.rf_address] = device
            device.metadata = device_metadata
        for room_metadata in message.rooms_metadata:
            if self.room_id_to_room.has_key(room_metadata.room_id):
                room = self.room_id_to_room[room_metadata.room_id]
            else:
                room = Room()
                self.room_id_to_room[room_metadata.room_id] = room
            room.metadata = room_metadata

    def handle_data_message(self, message):
        # find devices with given rf_addresses and update state with data from message
        for device_rf_address, device_state in message.contents.iteritems():
            if self.rf_address_to_device.has_key(device_rf_address):
                device = self.rf_address_to_device[device_rf_address]
                device.state = device_state
                print device_rf_address + ": " + device.until_raw() + ": " + str(device.until())

    def handle_config_message(self, message):
        # find device with given rf_address and update config with data from message
        if self.rf_address_to_device.has_key(message.rf_address):
            device = self.rf_address_to_device[message.rf_address]
            device.config = message.config

    def __repr__(self):
        return 'House[' \
               + repr(self.rf_address_to_device) + ',' \
               + repr(self.room_id_to_room) + ']'

    handlers = {
        messages.H_Message: lambda self, x: x,
        messages.L_Message: handle_data_message,
        messages.M_Message: handle_metadata_message,
        messages.C_Message: handle_config_message
    }

    device_types = {
        1: devices.HeatingThermostat,
        2: devices.HeatingThermostatPlus
    }


class Room(object):
    def __init__(self):
        self.metadata = None

    def __repr__(self):
        return 'Room[metadata=' + str(self.metadata) + ']'


class RoomMetadata(object):
    def __init__(self, room_id, name, rf_address):
        self.room_id = room_id
        self.name = name
        self.rf_address = rf_address

    def __repr__(self):
        return 'RoomMetadata[' \
               + str(self.room_id) + ',' \
               + self.name + ',' \
               + self.rf_address + ']'
