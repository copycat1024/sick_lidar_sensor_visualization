import socket
import inspect
from time import sleep

# main class to communicate with the MRS6000 sensor
class MRS6000:
    def __init__(self, ip, port):
        print('Start shell to Pidar sensor...')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        print('Done')
        print()

    def __del__(self):
        print('Closing shell to Pidar sensor')
        self.socket.close()
        print('Done')
        print()

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
        packet.print()

    def _send(self, cmd):
        self.socket.send(b'\x02' + cmd + b'\x03')

    def login(self):
        login_cmd = b'\x02sMN SetAccessMode 03 F4724744\x03'
        self.socket.send(login_cmd)
        data = self.socket.recv(1024)
        print(data)

    def macro(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()

        self._send(b'sMN LMCstartmeas')
        self._recv()

        self._send(b'sMN Run')
        self._recv()
        sleep(5)

        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()

        self._send(b'sMN LMCstopmeas')
        self._recv()

        self._send(b'sMN Run')
        self._recv()
        sleep(3)

        self._send(b'sRN LMDscandata')
        self._recv()

    def scan(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()

        self._send(b'sMN LMCstartmeas')
        self._recv()

        self._send(b'sMN Run')
        self._recv()
        
        while True:
            self._send(b'sRN LMDscandata')
            self._recv()

    def status(self):
        self._send(b'sRN STlms')
        self._recv()
        
    def test(self):
        self._send(b'sMN SetAccessMode 03 F4724744')
        self._recv()

class CoLaBPacket:
    def __init__(self, raw_data):
        if raw_data[0] != 2 and raw_data[-1] != 3:
            raise Exception('Wrong data type')
        args = [x.decode('UTF-8') for x in raw_data[1:-1].split(b' ')]

        self._i = -1
        self._data = args

        self.type = self.next()
        self.command = self.next()
        if self.type == 'sRA' and self.command == 'LMDscandata':

            f = open("scandata.bin","wb")
            f.write(bytearray(raw_data))

            self.version_number = self.next()

            self.device_number = self.next()
            self.serial_number = self.next()
            self.device_status = [self.next(), self.next()]

            self.telegram_counter = self.next()
            self.scan_counter = self.next()
            self.time_since_startup_in_us = self.next()
            self.time_of_transmission = self.next()
            self.status_of_digital_input = [self.next(), self.next()]
            self.status_of_digital_output = [self.next(), self.next()]
            self.layer_angle = self.next()

            self.scan_frequency = self.next()
            self.measurement_frequency = self.next()

            self.amount_of_encoder = self.next_int()
            if self.amount_of_encoder > 0:
                self.encoder_position = self.next()
                self.encoder_speed = self.next()

            self.amount_of_channel = self.next()

            # self.data = ''
            # for i in range(3, 24):
            #     self.data += '{} {}\n'.format(i, args[i])
        else:
            self.data = args[2:]

    def next(self):
        self._i += 1
        return self._data[self._i]

    def next_int(self):
        return int(self.next(), 16)

    def print(self):
        for key, value in self.__dict__.items():
            if key[0] != '_':
                print('{} : {}'.format(key.capitalize().replace('_', ' '), value))

        print()