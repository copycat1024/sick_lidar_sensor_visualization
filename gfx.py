from tkinter import Tk, Canvas, Frame, BOTH, ARC
from math import sin, cos, pi
from gfx_view import gfxView
from gfx_model import gfxModel

class gfxControl():
    def __init__(self, config):
        self.tk = Tk()
        self.tk.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.model = gfxModel(config)
        self.view = gfxView(self.tk, self.model)

        self.running = True
        self.last_scan = 0

    def draw(self, result):
        if self.last_scan < result.scan_counter:
            self.model.process_result(result)
            self.view.view_scan()
        self.tk.update_idletasks()
        self.tk.update()

    def draw_first(self):
        self.tk.update_idletasks()
        self.tk.update()
        self.view.view_first()
        self.tk.update_idletasks()
        self.tk.update()

    # when user close window
    def on_closing(self):
        self.running = False
