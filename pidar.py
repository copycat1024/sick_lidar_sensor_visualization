import socket
import inspect
from time import sleep, time_ns
from struct import unpack

# main class to communicate with the MRS6000 sensor
class MRS6000:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def __del__(self):
        self.socket.close()

    def _send(self, cmd):
        self.socket.send(b'\x02' + cmd + b'\x03')

    def _recv(self):
        End = b'\x03'
        total_data = []
        data = ''
        while True:
            data = self.socket.recv(8192)
            if End in data:
                total_data.append(data[:data.find(End)+1])
                break
            total_data.append(data)
        packet = CoLaBPacket(b''.join(total_data))
        return packet

    def config(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()

        # set output rate to 1 (no remission)
        self._send(b'sWN LMDscandatacfg 1F 0 0 1 0 0 0 0 0 0 0 1')
        self._recv()
        self._send(b'sMN Run')
        self._recv()

    def get_output_range(self):
        self._send(b'sRN LMPoutputRange')
        return self._recv()

    def start_scan(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()
        self._send(b'sMN LMCstartmeas')
        self._recv()
        self._send(b'sMN Run')
        self._recv()

        # 5 second start up time
        sleep(5)

    def scan_result(self):
        self._send(b'sRN LMDscandata')
        res = self._recv()
        sleep(0.01)
        return res

    def end_scan(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()
        self._send(b'sMN LMCstopmeas')
        self._recv()
        self._send(b'sMN Run')
        self._recv()


class CoLaBPacket:
    def __init__(self, raw_data):
        if raw_data[0] != 2 and raw_data[-1] != 3:
            raise Exception('Wrong data type')
        args = [x.decode('UTF-8') for x in raw_data[1:-1].split(b' ')]

        self._i = 0
        self._data = args

        self.type = self.next()
        self.command = self.next()
        if self.type == 'sRA' and self.command == 'LMDscandata':
            self._version_number = self.next()

            self._device_number = self.next()
            self._serial_number = self.next()
            self._device_status = self.next_pair()

            self.telegram_counter = self.next_int()
            self.scan_counter = self.next_int()
            self.time_since_startup = self.next_int()/1e6
            self.time_of_transmission = self.next_int()/1e6
            self._status_of_digital_input = self.next_pair()
            self._status_of_digital_output = self.next_pair()
            self.layer_angle = self.next_int()/200

            self.scan_frequency = self.next_int()/100
            self.measurement_frequency = self.next_int()/100

            self._amount_of_encoder = self.next_int()
            if self._amount_of_encoder > 0:
                self._encoder_position = self.next()
                self._encoder_speed = self.next()

            self.amount_of_channel = self.next_int()

            self.channel = dict()
            for _ in range(0, self.amount_of_channel):
                name, channel = self.next_channel()
                self.channel[name] = channel

        if self.type == 'sRA' and self.command == 'LMDscandatacfg':
            self.channel = self.next_pair()
            self.remission = self.next_int()
            self.resolution = self.next_int()
            self.unit = self.next_int()
            self.encoder = self.next_pair()
            self.position = self.next_int()
            self.device_name = self.next_int()
            self.comment = self.next_int()
            self.time = self.next_int()
            self.output_rate = self.next_pair()

        if self.type == 'sRA' and self.command == 'LMPoutputRange':
            self.number_of_sector = self.next_int()
            self.step_angle = self.next_int()/1e4
            self.start_angle = self.next_int()/1e4
            self.end_angle = self.next_int()/1e4

        self.remain = self.next_remain()

    def next_channel(self):
        name = self.next()
        channel = dict()
        channel['scale_factor'] = self.next_float()
        channel['scale_offset'] = self.next_float()
        channel['angle_start'] = self.next_int()/1e4
        channel['angle_step'] = self.next_int()/1e4
        channel['length'] = self.next_int()
        channel['data'] = self.next(channel['length'])
        return name, channel

    def next_pair(self):
        return ' '.join(self.next(2))

    def next_float(self):
        return unpack('!f', bytes.fromhex(self.next()))[0]
    def next_int(self):
        return int(self.next(), 16)

    def next_remain(self):
        return self.next(len(self._data)-self._i)

    def next(self, size=1):
        channel = self._data[self._i] if size == 1 else self._data[self._i:self._i + size]
        self._i += size
        return channel

    def print_pair(self, key, value):
        new_key = key.capitalize().replace('_', ' ')
        if isinstance(value, list):
            if len(value) > 5:
                print('{} : [... {} values]'.format(new_key, len(value)))
            else:
                print('{} : {}'.format(new_key, value))
        else:
            print('{} : {}'.format(new_key, value))

    def print(self):
        # if self.type == 'sRA' and self.command == 'LMDscandata':
        #     print(self.time_since_startup)
        #     print(self.time_of_transmission)
        #     print(self.measurement_frequency)
        #     print(self.hash)
        #     print()
        #     return

        for key, value in self.__dict__.items():
            if key[0] != '_':
                if isinstance(value, dict):
                    for key1, value1 in value.items():
                        self.print_pair(key, key1)
                        for key2, value2 in value1.items():
                            self.print_pair(key2, value2)
                else:
                    self.print_pair(key, value)

        print()
