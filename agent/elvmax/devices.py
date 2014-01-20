import messages
import datetime

class DeviceMetadata(object):
    def __init__(self, device_type, rf_address, serial, name, room_id):
        self.device_type = device_type
        self.rf_address = rf_address
        self.serial = serial
        self.name = name
        self.room_id = room_id

    def __repr__(self):
        return 'DeviceMetadata[' \
               + 'type:' + str(self.device_type) + ',' \
               + 'rf_address:' + self.rf_address + ',' \
               + 'serial:' + self.serial + ',' \
               + 'name:' + self.name + ',' \
               + 'room_id:' + str(self.room_id) + ']'


class Device(object):
    # NB: state and config getters should be specific for device type - need better doc
    class Mode(object):
        AUTO = 0
        MANUAL = 1
        VACATION = 2
        BOOST = 3

        @staticmethod
        def value_repr(value):
            return value and {0: "AUTO", 1: "MANUAL", 2: "VACATION", 3: "BOOST"}[value]

    def __init__(self):
        self.metadata = None
        self.state = None
        self.config = None

    def schedule_repr(self):
        return '\n'.join(
            '\t\t\t' + ' '.join(
                str(self.schedule_entry(t)) for t in range(day * 13, day * 13 + 13)
            ) for day in range(0, 7)
        )

    def __repr__(self):
        return 'Device[\n' \
               + '\tmetadata=' + str(self.metadata) + '\n' \
               + '\tstate:\n' \
               + '\t\tvalid:                ' + str(self.is_valid()) + '\n' \
               + '\t\terror:                ' + str(self.is_error()) + '\n' \
               + '\t\tnotification:         ' + str(self.is_notification()) + '\n' \
               + '\t\tinitialized:          ' + str(self.is_initialized()) + '\n' \
               + '\t\tbattery low:          ' + str(self.is_battery_low()) + '\n' \
               + '\t\tlink error:           ' + str(self.is_link_error()) + '\n' \
               + '\t\tpanel locked:         ' + str(self.is_panel_locked()) + '\n' \
               + '\t\tgateway known:        ' + str(self.is_gateway_known()) + '\n' \
               + '\t\tdst active:           ' + str(self.is_dst_active()) + '\n' \
               + '\t\tmode:                 ' + str(Device.Mode.value_repr(self.mode())) + '\n' \
               + '\t\tvalve position:       ' + str(self.valve_position()) + '\n' \
               + '\t\ttemperature:          ' + str(self.temperature()) + '\n' \
               + '\t\ttarget_temperature:   ' + str(self.target_temperature()) + '\n' \
               + '\t\tuntil:                ' + str(self.until()) + '\n' \
               + '\tconfig:\n' \
               + '\t\tcomfort temp:         ' + str(self.comfort_temperature()) + '\n' \
               + '\t\teco temp:             ' + str(self.eco_temperature()) + '\n' \
               + '\t\tmax temp:             ' + str(self.max_temperature()) + '\n' \
               + '\t\tmin temp:             ' + str(self.min_temperature()) + '\n' \
               + '\t\ttemp offset:          ' + str(self.temperature_offset()) + '\n' \
               + '\t\twindow open temp:     ' + str(self.window_open_temperature()) + '\n' \
               + '\t\twindow open duration: ' + str(self.window_open_duration()) + '\n' \
               + '\t\tboost duration:       ' + str(self.boost_duration()) + '\n' \
               + '\t\tboost valve value:    ' + str(self.boost_valve_value()) + '\n' \
               + '\t\tdecalcification day:  ' + str(self.decalcification_day()) + '\n' \
               + '\t\tdecalcification hour: ' + str(self.decalcification_hour()) + '\n' \
               + '\t\tmax valve value:      ' + str(self.max_valve_value()) + '\n' \
               + '\t\tvalve offset:         ' + str(self.valve_offset()) + '\n' \
               + '\t\tschedule:\n' + self.schedule_repr() \
               + ']'

    # State
    #
    # 0     1   message length
    # 1     3   radio address
    # 4  0  1   unknown
    # 5  1  2   bits
    # 7  3  1   valve position
    # 8  4  1   unknown
    # 9  5  2   temperature


    def is_valid(self):
        return self.state and bool(ord(self.state[1]) & 0x10)

    def is_error(self):
        return self.state and bool(ord(self.state[1]) & 0x08)

    def is_notification(self):
        return self.state and bool(ord(self.state[1]) & 0x04)

    def is_initialized(self):
        return self.state and bool(ord(self.state[1]) & 0x02)

    def is_battery_low(self):
        return self.state and bool(ord(self.state[2]) & 0x80)

    def is_link_error(self):
        return self.state and bool(ord(self.state[2]) & 0x40)

    def is_panel_locked(self):
        return self.state and bool(ord(self.state[2]) & 0x20)

    def is_gateway_known(self):
        return self.state and bool(ord(self.state[2]) & 0x10)

    def is_dst_active(self):
        return self.state and bool(ord(self.state[2]) & 0x08)

    # 0: Auto, 1: Manual, 2: Vacation, 3: Boost
    def mode(self):
        return ord(self.state[2]) & 0x03 if self.is_valid() else None

    def valve_position(self):
        return ord(self.state[3]) if self.is_valid() else None

    def target_temperature(self):
        return self.decode_temperature(ord(self.state[4])) if self.is_valid() else None

    def temperature(self):
        if self.until():
            return None
        else:
            return float((ord(self.state[5]) << 8) | ord(self.state[6]))/10.0

    def until(self):
        if self.is_valid():
            b1 = ord(self.state[5])
            b2 = ord(self.state[6])
            b3 = ord(self.state[7])
            year_delta = b2 & 0x7F
            month = ((b1 & 0xE0) << 1) + ((b2 & 0x80) >> 7)
            day = b1 & 0x1F
            if year_delta > 0 and month > 0 and day > 0:
                return datetime.datetime(
                    year_delta + 2000,
                    month,
                    day,
                    b3 / 2,
                    (b3 % 1) * 30
                )
            else:
                return None

        else:
            return None

    def until_raw(self):
        b1 = ord(self.state[5])
        b2 = ord(self.state[6])
        b3 = ord(self.state[7])

        return '%02x%02x%02x' % (b1, b2, b3)

    # Config

    def comfort_temperature(self):
        return self.config and self.decode_temperature(ord(self.config[0x12]))

    def eco_temperature(self):
        return self.config and self.decode_temperature(ord(self.config[0x13]))

    def max_temperature(self):
        return self.config and self.decode_temperature(ord(self.config[0x14]))

    def min_temperature(self):
        return self.config and self.decode_temperature(ord(self.config[0x15]))

    def temperature_offset(self):
        """ default temperature offset value is 7 (0C), range 0-14 (-3.5 to +3.5)  """
        return self.config and self.decode_temperature(ord(self.config[0x16])) - 3.5

    def window_open_temperature(self):
        return self.config and self.decode_temperature(ord(self.config[0x17]))

    def window_open_duration(self):
        return self.config and ord(self.config[0x18])

    def boost_duration(self):
        """ Range: 0-7, Value in %: value*5 min, except 7: 30 min """
        return self.config and ord(self.config[0x19]) >> 5

    def boost_valve_value(self):
        """ Range: 0-20, Value in %: value*5 """
        return self.config and ord(self.config[0x19]) & 0x1F

    def decalcification_day(self):
        """ 1: Sat, 7: Fri """
        return self.config and ord(self.config[0x1A]) >> 5

    def decalcification_hour(self):
        return self.config and ord(self.config[0x1A]) & 0x1F

    def max_valve_value(self):
        """ Range: 0-0xFF, corresponds to 0-100% """
        return self.config and ord(self.config[0x1B])

    def valve_offset(self):
        """ Range: 0-0xFF, corresponds to 0-100% """
        return self.config and ord(self.config[0x1C])

    def schedule_entry(self, t):
        """ Range: 13*7 elements, 13 entries per day for 7 days, start from Saturday """
        return self.config and (self.decode_temperature(ord(self.config[0x1D + 2*t]) >> 1), (((ord(self.config[0x1D + 2*t]) & 0x01) << 8) | ord(self.config[0x1E + 2*t]))*5)

    def decode_temperature(self, value):
        return value / 2.0


class HeatingThermostat(Device):
    def __repr__(self):
        return 'HeatingThermostat:' + super(HeatingThermostat, self).__repr__()

    def command_set_temperature(self, mode_value, temperature=None, year=None, month=None, day=None, half_our_units=None):
        """ mode: 0=Auto, 1=Permanent(tested: Manual), 2=Temporarily(tested: Vacation?), 3=Boost """
        messages.command_set_temperature(
            self.metadata.rf_address,
            self.metadata.room_id,
            mode_value,
            temperature,
            year,
            month,
            day,
            half_our_units
        )

class HeatingThermostatPlus(Device):
    def __repr__(self):
        return 'HeatingThermostatPlus:' + super(HeatingThermostatPlus, self).__repr__()
