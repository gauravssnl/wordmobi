# -*- coding: utf-8 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3
import e32
import graphics
import key_codes
from appuifw import *
import sysinfo
import ctoolbar
import time

class ToolbarDemo(object):
    """ Scribble demo for touch UI
    """
    def __init__(self):       
        self.lock = e32.Ao_lock()
        app.title = u"Scribble"
        app.screen = "full_max"
        self.maintb = None
        self.ticktb = None
        self.colortb = None
        self.line_colors = [(0,0,255),(0,128,0),(255,255,0),
                            (255,255,255),(255,0,0)]
        self.line_color = 0
        self.line_ticks = [1,3,6]
        self.line_tick = 0
        self.prev_x = 0
        self.prev_y = 0
        self.saving = False
        self.drag_started = False
        self.load_imgs()
        sz = max(sysinfo.display_pixels())
        self.drw_buf = graphics.Image.new((sz,sz))
        self.scr_buf = graphics.Image.new((sz,sz))
        self.drw_buf.clear((255,255,255))
        self.canvas = Canvas(redraw_callback=self.redraw,
                             event_callback=self.event)
        self.maintb = ctoolbar.CanvasToolbar(self.scr_buf,
                                             self.maintb_selected,
                                             self.redraw,
                                             self.maintb_imgs,
                                             (0,0),
                                             (200,200,200),
                                             transparency=20)
        self.ticktb = ctoolbar.CanvasToolbar(self.scr_buf,
                                             self.ticktb_selected,
                                             self.redraw,
                                             self.ticktb_imgs,
                                             (54,97),
                                             (200,200,200),
                                             orientation=ctoolbar.O_HORIZONTAL,
                                             transparency=20)
        self.colortb = ctoolbar.CanvasToolbar(self.scr_buf,
                                              self.colortb_selected,
                                              self.redraw,
                                              self.colortb_imgs,
                                              (54,145),
                                              (200,200,200),
                                              orientation=ctoolbar.O_HORIZONTAL,
                                              transparency=20)
        app.body = self.canvas
        app.menu = []
        self.maintb.show()
        self.lock.wait()

    def load_imgs(self):
        imgs_file = [ u"e:\\python\\new44.png",
                      u"e:\\python\\save44.png",
                      u"e:\\python\\line44.png",
                      u"e:\\python\\color44.png",
                      u"e:\\python\\about44.png",
                      u"e:\\python\\close44.png"]
        self.maintb_imgs = []
        for fn in imgs_file:
            self.maintb_imgs.append(graphics.Image.open(fn))

        imgs_file = [ u"e:\\python\\ticka44.png",
                      u"e:\\python\\tickb44.png",
                      u"e:\\python\\tickc44.png" ]
        self.ticktb_imgs = []
        for fn in imgs_file:
            self.ticktb_imgs.append(graphics.Image.open(fn))

        imgs_file = [ u"e:\\python\\cblue44.png",
                      u"e:\\python\\cgreen44.png",
                      u"e:\\python\\cyellow44.png",
                      u"e:\\python\\cwhite44.png",
                      u"e:\\python\\cred44.png" ]
        self.colortb_imgs = []
        for fn in imgs_file:
            self.colortb_imgs.append(graphics.Image.open(fn))

    def event(self,ev):
        # just checking touch events
        if not ev['type'] in [key_codes.EButton1Up,
                              key_codes.EButton1Down,
                              key_codes.EDrag]:
            return
        # Did the even happen inside any toolbar ?
        mtb = self.maintb.is_inside(ev['pos']) and self.maintb.is_visible()
        ttb = self.ticktb.is_inside(ev['pos']) and self.ticktb.is_visible()
        ctb = self.colortb.is_inside(ev['pos']) and self.colortb.is_visible()
        int_tlb = mtb or ttb or ctb
        # reset any drag indication if othe event takes place
        if ev['type'] != key_codes.EDrag:
            self.drag_started = False
        # toolbar clicks
        if int_tlb and (ev['type'] == key_codes.EButton1Down):
            if mtb:
                self.maintb.set_sel(ev['pos'])
            elif ttb:
                self.ticktb.set_sel(ev['pos'])
            elif ctb:
                self.colortb.set_sel(ev['pos'])
        # drag inside toolbar or click or drag outside toolbar
        elif (int_tlb and (ev['type'] != key_codes.EButton1Down)) or (not int_tlb):
            # clicks outside toolbar
            if ev['type'] == key_codes.EButton1Down:
                self.drw_buf.point((ev['pos'][0], ev['pos'][1]),
                                   outline=self.line_colors[self.line_color],
                                   width=self.line_ticks[self.line_tick],
                                   fill=self.line_colors[self.line_color])
            # drags, inside or outside toolbars
            elif ev['type'] == key_codes.EDrag:
                # do not start drag inside toolbars, only outside !
                if self.drag_started or (not int_tlb):
                    self.drag_started = True
                    rect = (self.prev_x, self.prev_y, ev['pos'][0], ev['pos'][1])
                    # draw on canvas and into buffer, this way it is not necessary to call
                    # an explicit redraw
                    self.canvas.line(rect,
                                     outline=self.line_colors[self.line_color],
                                     width=self.line_ticks[self.line_tick],
                                     fill=self.line_colors[self.line_color])
                    self.drw_buf.line(rect,
                                      outline=self.line_colors[self.line_color],
                                      width=self.line_ticks[self.line_tick],
                                      fill=self.line_colors[self.line_color])
        # always save last position for drag operations
        self.prev_x = ev['pos'][0]
        self.prev_y = ev['pos'][1]

    def redraw(self,rect=None):
        """ Erase your canvas, draw your stuff and
            ask toolbar for redrawing if it is visible.
            Finally, blit your buffer in canvas.
        """
        self.scr_buf.clear((255,255,255))
        self.scr_buf.blit(self.drw_buf)
        if self.maintb and self.ticktb and self.colortb:
            self.maintb.redraw()
            if self.ticktb.is_visible():
                self.ticktb.redraw()
            if self.colortb.is_visible():
                self.colortb.redraw()
        self.canvas.blit(self.scr_buf)

    def maintb_selected(self):
        item = self.maintb.get_sel()
        if item == 0:
            self.new_img()
        elif item == 1:
            self.save_img()
        elif item == 2:
            if self.ticktb.is_visible():
                self.ticktb.hide()
            else:
                self.ticktb.show()
        elif item == 3:
            if self.colortb.is_visible():
                self.colortb.hide()
            else:
                self.colortb.show()
        elif item == 4:
            self.about()
        elif item == 5:
            self.close_app()

    def ticktb_selected(self):
        self.line_tick = self.ticktb.get_sel()
        
    def colortb_selected(self):
        self.line_color = self.colortb.get_sel()

    def new_img(self):
        self.drw_buf.clear((255,255,255))
        self.redraw()

    def save_img(self):
        if not self.saving:
            self.saving = True
            fn = time.strftime(u"e:\\%d%m%Y%H%M%S.jpg", time.localtime())
            img = graphics.Image.new(self.canvas.size)
            img.blit(self.drw_buf)
            img.save(fn,quality=100)
            note(fn+u" saved.","info")
            self.saving = False
            
    def about(self):
        note(u"Scribble toolbar demo by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def close_app(self):
        self.lock.signal()
        app.set_exit()

ToolbarDemo()
