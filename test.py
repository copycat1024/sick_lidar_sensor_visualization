import socket
import inspect
import sys
from time import sleep

PIDAR_IP = '192.168.69.245'
PIDAR_PORT = 2111


class Pidar:
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
            print(data)
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data) > 1:
                # check if end_of_data was split
                last_pair = total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2] = last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
        print(total_data)

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


def prompt(txt):
    print('> ', end='')
    sys.stdout.flush()


if __name__ == '__main__':
    cmd = [x[0] for x in inspect.getmembers(Pidar) if x[0][0] != '_']
    sensor = Pidar(PIDAR_IP, PIDAR_PORT)
    try:
        prompt('> ')
        for line in sys.stdin:
            line = line.rstrip()
            if line == 'exit':
                break
            elif line in cmd:
                getattr(sensor, line)()
            else:
                print('Command \'{}\' not found'.format(line))
            prompt('> ')

    except KeyboardInterrupt:
        pass
