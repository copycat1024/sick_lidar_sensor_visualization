import inspect
import sys
from pidar import MRS6000

PIDAR_IP = '192.168.69.245'
PIDAR_PORT = 2111

def prompt(txt):
    print('> ', end='')
    sys.stdout.flush()

if __name__ == '__main__':
    cmd = [x[0] for x in inspect.getmembers(MRS6000) if x[0][0] != '_']
    sensor = MRS6000(PIDAR_IP, PIDAR_PORT)
    
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
