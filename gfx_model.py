from math import sin, cos, pi
from gfx_view import deg2rad, in_rec, WARNING, DANGER, SAFE

class gfxModel:
    def __init__(self, config):
        sensor = config['sensor']
        self.ip = sensor['ip']
        self.port = sensor['port']

        display = config['display']

        # size per one grid arc (mm)
        self.grid = display['grid']
        # max distance (mm)
        self.max = display['max']
        # angle resolution (degree)
        self.angle_resolution = display['resolution']
        # sensor size (radius, in mm)
        self.sensor_size = display['sensor_size']
        self.margin = display['margin']

        detect = config['detect']
        self.trigger_count = detect['count']
        self.detect_count = dict()
        self.reset_detect_count()
        self.detect_zones = list()
        self.detect_zones.extend([(x, DANGER) for x in detect['danger']])
        self.detect_zones.extend([(x, WARNING) for x in detect['warning']])
        self.detect_color = SAFE

    # process result from the sensor into data
    def process_result(self, result):
        raw = self.extract(result)
        self.data = self.oversample(raw, self.angle_resolution)
        self.zones, self.detect_color = self.detect_zone()

    # extract raw data, also update config
    def extract(self, result):
        # distance channel 1
        channel = result.channel['DIST1']

        # value = A*x + B
        A = channel['scale_factor']*cos(result.layer_angle*pi/180)
        B = channel['scale_offset']

        # extracting the data
        points = list()
        for i in range(0, channel['length']):
            x = int(channel['data'][i], 16)
            if x >= 16:  # value under 16 is invalid data
                value = (A*x + B)
                phi = channel['angle_start'] + i*channel['angle_step']
                points.append((value, phi))

        # side effect, update config
        self.angle = (
            channel['angle_start'],
            channel['angle_start'] + channel['length']*channel['angle_step']
        )
        self.min = A*16 + B
        return points

    # take avarage value of one small cone
    def oversample(self, points, resolution):
        if resolution == 0:
            return points
        angle_i = 0
        i = 0
        new_points = list()
        while i < len(points):
            while angle_i < points[i][1]:
                angle_i += resolution
            sum_phi = 0
            sum_value = 0
            count = 0
            while points[i][1] <= angle_i:
                sum_value += points[i][0]
                sum_phi += points[i][1]
                count += 1
                i += 1
                if i >= len(points):
                    break
            new_points.append((sum_value/count, sum_phi/count))
        return new_points

    def detect_zone(self):
        points = list()
        for value, angle in self.data:
            phi = deg2rad(angle)
            x = value*cos(phi)
            y = value*sin(phi)
            points.append((x, y))
        zones = list()
        self.reset_detect_count()
        for zone, unsafe_color in self.detect_zones:
            count = 0
            for p in points:
                if in_rec(*p, *zone):
                    count += 1
            if count > self.trigger_count:
                color = unsafe_color
                self.detect_count[unsafe_color] += 1
            else:
                color = SAFE
            zones.append((zone, color))
        detect_color = SAFE
        if self.detect_count[DANGER] > 0:
            detect_color = DANGER
        elif self.detect_count[WARNING] > 0:
            detect_color = WARNING
        return zones, detect_color

    def reset_detect_count(self):
        self.detect_count[DANGER] = 0
        self.detect_count[WARNING] = 0
