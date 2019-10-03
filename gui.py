from gfx import gfxControl
from gfx_model import DANGER, WARNING, SAFE
from pidar import MRS6000
from time import sleep
import toml
from playsound import playsound
from threading import Thread

def sound_alarm(name):
    playsound(name+'.wav')

def main():
    config = toml.load('config.toml')
    sensor = config['sensor']
    PIDAR_IP = sensor['ip']
    PIDAR_PORT = sensor['port']

    gfx = gfxControl(config)
    gfx.draw_first()
    sensor = MRS6000(PIDAR_IP, PIDAR_PORT)

    sensor.config()
    sensor.start_scan()

    alarm = Thread()
    while gfx.running:
        gfx.draw(sensor.scan_result())
        if not alarm.is_alive() and gfx.model.detect_color != SAFE:
            name = 'danger' if gfx.model.detect_color == DANGER else 'warning'
            alarm = Thread(target=sound_alarm, args=(name,))
            alarm.start()
        sleep(0.1)
    sensor.end_scan()

if __name__ == '__main__':
    main()
