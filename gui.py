from gfx import gfxControl
from pidar import MRS6000
from time import sleep

PIDAR_IP = '192.168.69.245'
PIDAR_PORT = 2111

def main():
    gfx = gfxControl()
    gfx.draw_first()
    sensor = MRS6000(PIDAR_IP, PIDAR_PORT)

    sensor.start_scan()
    while gfx.running:
        gfx.draw(sensor.scan_result())
        sleep(0.1)
    sensor.end_scan()


if __name__ == '__main__':
    main()
