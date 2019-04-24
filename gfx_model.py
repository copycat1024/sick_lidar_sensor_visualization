from math import sin, cos, pi


class gfxModel:
    def __init__(self):
        # size per one grid arc (mm)
        self.grid = 1000
        # max distance (mm)
        self.max = 5000
        # angle resolution (degree)
        self.angle_resolution = 0
        # sensor size (radius, in mm)
        self.sensor_size = 80

        self.zones = list()
        self.zones.extend([(-800, x, 0, x+800) for x in range(800, 3600, 800)])
        self.zones.extend([(0, x, 800, x+800) for x in range(800, 3600, 800)])

    # process result from the sensor into data
    def process_result(self, result):
        raw = self.extract(result)
        self.data = self.oversample(raw, self.angle_resolution)

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
