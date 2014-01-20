import base64
import datetime
import devices
import house


class Message(object):
    def read_byte(self, it):
        return ord(it.next())

    def read_string(self, it):
        length = ord(it.next())
        return "".join([it.next() for j in range(0, length)])

    def read_serial(self, it):
        return ''.join('%02x' % ord(it.next()) for j in range(0, 10))

    def read_hex_string(self, it, count):
        return ''.join('%02x' % ord(it.next()) for j in range(0, count))


class H_Message(Message):
    def __init__(self, string):
        strings = string.split(',')
        self.serial = strings[0]
        self.rf_address = strings[1]
        self.firmware = strings[2]
        self.unknown = strings[3]
        self.connection_id = strings[4]
        self.date_time = self.parse_date_time(strings[7], strings[8])

    def __repr__(self):
        return 'Hello[' \
               + self.serial + ',' \
               + self.rf_address + ',' \
               + self.firmware + ',' \
               + self.unknown + ',' \
               + self.connection_id + ',' \
               + str(self.date_time) + ']'

    def parse_date_time(self, date, time):
        return datetime.datetime(
            int(date[0:2], 16) + 2000,
            int(date[2:4], 16),
            int(date[4:6], 16),
            int(time[0:2], 16),
            int(time[2:4], 16)
        )


class M_Message(Message):

    def __init__(self, string):
        strings = string.split(',')
        if len(strings) != 3:
            raise ValueError()
        self.index = int(strings[0], 16)
        self.count = int(strings[1], 16)
        self.rooms_metadata = []
        self.devices_metadata = []

        data = base64.b64decode(strings[2])
        it = iter(data)
        self.read_byte(it)
        self.read_byte(it)

        # parse rooms
        room_count = ord(it.next())
        for room_index in range(0, room_count):
            room_metadata = house.RoomMetadata(
                self.read_byte(it),
                self.read_string(it),
                self.read_hex_string(it, 3))
            self.rooms_metadata += [room_metadata]

        # parse devices
        device_count = ord(it.next())
        for device_index in range(0, device_count):
            device_metadata = devices.DeviceMetadata(
                self.read_byte(it),
                self.read_hex_string(it, 3),
                self.read_serial(it),
                self.read_string(it),
                self.read_byte(it)
            )
            self.devices_metadata += [device_metadata]

    def __repr__(self):
        return 'Metadata\n'\
               + '\tIndex:\t' + str(self.index) + '\n'\
               + '\tCount:\t' + str(self.count) + '\n'\
               + '\tRooms:\t' + ",".join(str(room) for room in self.rooms_metadata) + '\n' \
               + '\tDevices:\t' + ",".join(str(device) for device in self.devices_metadata)


class C_Message(Message):

    def __init__(self, string):
        strings = string.split(',')
        if len(strings) != 2:
            raise ValueError()
        self.rf_address = strings[0]
        self.config = base64.b64decode(strings[1])

    def __repr__(self):
        return 'Configuration: address='+ str(self.rf_address)


class L_Message(Message):

    def __init__(self, string):
        data = base64.b64decode(string)
        tokens = self.tokenize(data)
        self.contents = {
            '%02x%02x%02x' % (ord(token[0]), ord(token[1]), ord(token[2])) : token[3:]
            for token in tokens
        }   # map {string rf_address: bytes device_state}

    def tokenize(self, data):
        """ data format: [length1:1][token1:length1][length2:1][token2:length2]... """
        i = 0
        tokens = []
        len1 = len(data)
        while i < len1:
            length = ord(data[i])
            start = i + 1
            i = start + length
            tokens += [data[start:i]]
        return tokens

    def __repr__(self):
        return 'Data:' + str(self.contents) + '\n'


# INCOMING_HELLO = "H:"
# INCOMING_FAILURE = "F:"
# INCOMING_DEVICE_LIST = "L:"
# INCOMING_CONFIGURATION = "C:"
# INCOMING_METADATA = "M:"
# INCOMING_NEW_DEVICE = "N:"
# INCOMING_ACKNOWLEDGE = "A:"
# INCOMING_ENCRYPTION = "E:"
# INCOMING_DECRYPTION = "D:"
# INCOMING_SET_CREDENTIALS = "b:"
# INCOMING_GET_CREDENTIALS = "g:"
# INCOMING_SET_REMOTE_ACCESS = "j:"
# INCOMING_SET_USER_DATA = "p:"
# INCOMING_GET_USER_DATA = "o:"
# INCOMING_SEND_DEVICE_CMD = "S:"

# S: response format: <DutyCycle (hex)>, <CommandDiscarded (1 or 0)>, <FreeMemorySlot (hex)>
response_types = {
    'H': H_Message,
    'M': M_Message,
    'L': L_Message,
    'C': C_Message
}


class request_types:
    RESET = 'a'
    NTP_SERVER = 'f'
    GET_CONFIGURATION = 'c'
    GET_DEVICE_LIST = 'l'
    URL = 'u'
    INTERVAL = 'i'
    METADATA = 'm'
    INCLUSION_MODE = 'n'
    CANCEL_INCLUSION_MODE = 'x'
    MORE_DATA = 'g'
    QUIT = 'q'
    ENCRYPTION = 'e'
    DECRYPTION = 'd'
    SET_CREDENTIALS = 'B'
    GET_CREDENTIALS = 'G'
    SET_REMOTE_ACCESS = 'J'
    SET_USER_DATA = 'P'
    GET_USER_DATA = 'O'
    ACTIVATE_PRODUCT = 'W'
    SEND_DEVICE_CMD = 's'
    RESET_ERROR = 'r'
    DELETE_DEVICES = 't'
    SET_PUSHBUTTON_CONFIG = 'w'
    SET_URL = 'u'
    TIME_CONFIG = 'v'
    SEND_WAKEUP = 'z'


def command_set_temperature(rf_address, room_number, mode_value, temperature=None , year=None, month=None, day=None, half_our_units=None):
    """
    mode: 0=Auto, 1=Permanent, 2=Temporarily
    date and time until: zeroes, year 2000 => no end time
    tested with mode 0 (Auto), 1 (Permanent)
    """
    has_time = year and month and day and half_our_units
    data = bytearray(14 if has_time else 11)
    data[0] = 0x00
    data[1] = 0x04
    data[2] = 0x40
    data[3] = 0x00
    data[4] = 0x00
    data[5] = 0x00
    data[6] = int(rf_address[0:2], 16)
    data[7] = int(rf_address[2:4], 16)
    data[8] = int(rf_address[4:6], 16)
    data[9] = int(room_number)
    data[10] = (int(temperature * 2.0) | (mode_value << 6)) if mode_value > 0 else 0
    # data[10] = ((int(temperature * 2.0) << 2) | mode_value) if mode_value > 0 else 0
    if has_time:
        data[11] = ((month >> 1) << 5) | day
        data[12] = ((month & 1) << 7) | (year - 2000)
        data[13] = half_our_units
    return command(request_types.SEND_DEVICE_CMD, base64.b64encode(str(data)))

def command(request_type, payload=''):
    return request_type + ':' + payload
