from tkinter import Tk, Canvas, Frame, BOTH, ARC, PIESLICE
from math import sin, cos, pi, tan

# color
WARNING = '#ff0'
DANGER = '#f44'
SAFE = '#4f4'

class gfxView():
    def __init__(self, tk, model):
        tk.title('Lidar. IP: {}. Port: {}'.format(model.ip, model.port))
        tk.geometry('800x600+10+10')

        self.canvas = Canvas(tk)
        self.canvas.pack(fill=BOTH, expand=1)
        self.model = model

    # view the window at the start
    def view_first(self):
        self.prepare_view()
        self.rec(*self.frame, fill='white', outline='')
        self.draw_frame()
        for zone, color in self.model.detect_zones:
            self.rec_zone(zone, fill=color)
        self.draw_grid()

    # view result of a scan
    def view_scan(self):
        self.prepare_view()
        self.draw_bg()
        self.draw_zones()
        self.draw_grid()
        self.draw_frame()
        self.draw_data()

    def prepare_view(self):
        # get canvas size
        H = self.canvas.winfo_height()
        W = self.canvas.winfo_width()

        # margin
        self.M = self.model.margin

        # spagetti sauce
        H -= self.M

        # radius
        if 2*H > W:
            self.R = W/2
        else:
            self.R = H

        # center of sensor view
        self.x0 = self.R
        self.y0 = self.R
        self.center = (self.x0, self.y0)

        # frame of sensor view
        self.frame = (self.M, self.M, 2*self.R-self.M, self.R)

        # scale_factor
        self.scale = (self.R-self.M) / self.model.max

        # clear canvas
        self.canvas.delete('all')

    # draw the background
    def draw_bg(self):
        self.rec(*self.frame, fill='white', outline='')
        self.draw_cone(*self.model.angle, self.model.min)

    # draw the detecting zone
    def draw_zones(self):
        for zone, color in self.model.zones:
            self.rec_zone(zone, fill=color)

    # draw the data points
    def draw_data(self):
        for value, phi in self.model.data:
            # scale value to graph
            v = value * self.scale
            x, y = self.pol2car(v, phi)
            if in_rec(x, y, *self.frame):
                self.point(x, y, outline='', fill='blue')

    # draw the frame of the sensor view
    def draw_frame(self):
        self.rec(*self.frame)
        sr = self.model.sensor_size * self.scale
        if sr < 1:
            sr = 1
        self.cir(*self.center, sr, fill='blue')

    # draw sensor's cone of view
    def draw_cone(self, a0, a1, min):
        x0, y0, x1, _ = self.frame
        xp0, yp0, p0 = self.angle_intersect(a0)
        xp1, yp1, p1 = self.angle_intersect(a1)

        poly = list()
        poly.extend(self.center)
        poly.extend((xp0, yp0))
        if in_range(x1, p1, p0):
            poly.extend((x1, y0))
        if in_range(x0, p1, p0):
            poly.extend((x0, y0))
        poly.extend((xp1, yp1))
        self.canvas.create_polygon(*poly, fill=self.model.detect_color)
        self.arc(min*self.scale, a0, a1, style=PIESLICE,
                 fill='white', outline='')

    # draw grid on the sensor view
    def draw_grid(self):
        for i in range(0, self.model.max, self.model.grid):
            r_i = (i + self.model.grid)*self.scale
            l_i = (i + self.model.grid)*1e-3
            self.canvas.create_text(self.R+r_i, self.R+20, text=str(l_i))
            self.canvas.create_text(self.R-r_i, self.R+20, text=str(l_i))
            self.arc(r_i, 0, 180, style=ARC)

    # check intersect of a line from the center to the edge of the sensor view
    def angle_intersect(self, a):
        x0, y0, x1, y1 = self.frame
        t = tan(deg2rad(a))
        xcen = (x1+x0)/2
        xlen = (x1-x0)/2
        x = xcen*(1 + 1/t)
        if x < x0:
            return x0, y1 + xlen*t, x
        if x > x1:
            return x1, y1 - xlen*t, x
        return x, y0, x

    # draw rectangle of detection zone
    def rec_zone(self, zone, *args, **kwargs):
        x0, y0, x1, y1 = zone
        nx0 = self.R + x0*self.scale
        nx1 = self.R + x1*self.scale
        ny0 = self.R - y0*self.scale
        ny1 = self.R - y1*self.scale
        self.rec(nx0, ny0, nx1, ny1, *args, **kwargs)

    # draw line
    def line(self, x0, y0, x1, y1, *args, **kwargs):
        self.canvas.create_line(x0, y0, x1, y1, *args, **kwargs)

    # draw point
    def point(self, x, y, *args, **kwargs):
        self.cir(x, y, 2, *args, **kwargs)

    # draw circle
    def cir(self, x, y, r, *args, **kwargs):
        self.canvas.create_oval(cen2rec(x, y, r), *args, **kwargs)

    # draw arc
    def arc(self, r, start_angle, end_angle, *args, **kwargs):
        phi = end_angle
        d_phi = start_angle - end_angle
        self.canvas.create_arc(cen2rec(self.x0, self.y0, r),
                               start=phi, extent=d_phi, *args, **kwargs)

    def rec(self, x0, y0, x1, y1, *args, **kwargs):
        self.canvas.create_rectangle(x0, y0, x1, y1, *args, **kwargs)

    # convert from polar to cartesian coordinate
    def pol2car(self, r, angle):
        phi = deg2rad(angle)
        return self.x0 + r*cos(phi), self.y0 - r*sin(phi)

# degree to radian


def deg2rad(a):
    return a * pi / 180

# center coordinate to rectangular coordinate


def cen2rec(x0, y0, r):
    return x0 - r, y0 - r, x0 + r, y0 + r

# check if point lie in a rectangle


def in_rec(x, y, x0, y0, x1, y1):
    return in_range(x, x0, x1) and in_range(y, y0, y1)

# check if value is between two order value


def in_range(x, x0, x1):
    return x >= x0 and x <= x1
