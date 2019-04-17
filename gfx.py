from tkinter import Tk, Canvas, Frame, BOTH, ARC
from math import sin, cos, pi


class gfxMain():
    def __init__(self):
        self.tk = Tk()
        self.tk.title('Lidar')
        self.tk.geometry('800x600+10+10')
        self.tk.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.canvas = Canvas(self.tk)
        self.canvas.pack(fill=BOTH, expand=1)

        self.running = True
        self.last_scan = 0
        # radius
        self.R = 400
        # margin
        self.M = 50
        # number of grid arc
        self.G = 4
        # max distance (mm)
        self.D = 2000

    def init_cone(self, angle):
        self.start_angle = angle.start_angle
        self.end_angle = angle.end_angle

    def draw(self, result):
        self.canvas.delete('all')
        self.draw_cone()
        if self.last_scan < result.scan_counter:
            self.draw_scan(result)
        self.tk.update_idletasks()
        self.tk.update()

    def draw_scan(self, result):
        channel = result.channel['DIST1']
        # value = a*x + b
        A = channel['scale_factor']*cos(result.layer_angle*pi/180)
        B = channel['scale_offset']
        for i in range(0, channel['length']):
            x = int(channel['data'][i], 16)
            value = (A*x + B) * (self.R-self.M) / self.D
            phi = channel['angle_start'] + i*channel['angle_step']
            self.ppoint(self.R, self.R, value, phi)

    def draw_cone(self):
        self.pline(self.R, self.R, self.R-self.M, self.start_angle)
        self.pline(self.R, self.R, self.R-self.M, self.end_angle)
        self.circle(self.R, self.R, 20)
        for i in range(1, self.G+1):
            self.arc(self.R, self.R, (self.R-self.M)*i /
                     self.G, self.start_angle, self.end_angle)

    # polar line
    def pline(self, x0, y0, r, angle):
        phi = angle * pi / 180
        self.canvas.create_line(x0, y0, x0 + r*cos(phi), y0 - r*sin(phi))

    # polar point
    def ppoint(self, x0, y0, r, angle):
        phi = angle * pi / 180
        self.canvas.create_line(x0 + r*cos(phi), y0 -
                                r*sin(phi), x0 + r*cos(phi) + 1, y0 - r*sin(phi) + 1)

    def circle(self, x0, y0, r):
        self.canvas.create_oval(self.cen2rec(x0, y0, r))

    def arc(self, x0, y0, r, start_angle, end_angle):
        phi = end_angle
        d_phi = start_angle - end_angle
        self.canvas.create_arc(self.cen2rec(x0, y0, r),
                               start=phi, extent=d_phi, style=ARC)

    def cen2rec(self, x0, y0, r):
        return x0 - r, y0 - r, x0 + r, y0 + r

    def on_closing(self):
        self.running = False
