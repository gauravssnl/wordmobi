# -*- coding: utf-8 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3
import e32
import graphics
import key_codes
from appuifw import *
import sysinfo
from ctoolbar import CanvasToolbar

class ToolbarDemo(object):
    """ Toolbar demo for non touch UI
    """
    def __init__(self):       
        self.lock = e32.Ao_lock()
        app.title = u"ToolbarDemo"
        app.screen = "full"
        self.toolbar = None
        self.load_imgs()
        sz = max(sysinfo.display_pixels())
        self.scr_buf = graphics.Image.new((sz,sz))        
        self.canvas = Canvas(redraw_callback=self.redraw)
        self.toolbar = CanvasToolbar(self.scr_buf,
                                     self.item_selected,
                                     self.redraw,
                                     self.imgs,
                                     (0,0))
        app.body = self.canvas
        app.menu = [(u"Show toolbar", lambda: self.toolbar.show()),
                    (u"Hide toolbar", lambda: self.toolbar.hide()),
                    (u"Help", self.help),
                    (u"About", self.about),
                    (u"Quit", self.close_app)]
        self.toolbar.show()
        self.canvas.bind(key_codes.EKeyLeftArrow,self.left_key)
        self.canvas.bind(key_codes.EKeyUpArrow,self.up_key)
        self.canvas.bind(key_codes.EKeyDownArrow,self.down_key)
        self.canvas.bind(key_codes.EKeySelect,self.sel_key)
        self.lock.wait()

    def left_key(self):
        if not self.toolbar.is_visible():
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def up_key(self):
        if self.toolbar.is_visible():
            self.toolbar.prev()

    def down_key(self):
        if self.toolbar.is_visible():
            self.toolbar.next()

    def sel_key(self):
        if self.toolbar.is_visible():
            self.toolbar.set_sel()

    def redraw(self,rect=None):
        """ Erase your canvas, draw your stuff and
            ask toolbar for redrawing if it is visible.
            Finally, blit your buffer in canvas.
        """
        self.scr_buf.clear((255,255,255))
        if self.toolbar:
            self.toolbar.redraw()
        self.canvas.blit(self.scr_buf)
        
    def load_imgs(self):
        imgs_file = [ u"e:\\python\\refresh22.png",
                      u"e:\\python\\day22.png",
                      u"e:\\python\\week22.png",
                      u"e:\\python\\month22.png",
                      u"e:\\python\\setup22.png" ]

        self.imgs = []
        for fn in imgs_file:
            self.imgs.append(graphics.Image.open(fn))

    def item_selected(self):
        item = self.toolbar.get_sel()
        if item == -1:
            note(u"No item selected","info")
        else:
            note(u"Item %d selected" % item,"info")

    def help(self):
        note(u"Left arrow to show/hide the toolbar","info")

    def about(self):
        note(u"Canvas toolbar demo by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def close_app(self):
        self.lock.signal()
        app.set_exit()

ToolbarDemo()
