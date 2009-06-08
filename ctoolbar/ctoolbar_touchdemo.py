import e32
import graphics
import key_codes
from appuifw import *
import sysinfo
from ctoolbar import CanvasToolbar

class ToolbarDemo(object):
    """ Toolbar demo for touch UI
    """
    def __init__(self):       
        self.lock = e32.Ao_lock()
        app.title = u"ToolbarDemo"
        app.screen = "full"
        self.toolbar = None
        self.drag_filter_cnt = 0
        self.load_imgs()
        sz = max(sysinfo.display_pixels())
        self.scr_buf = graphics.Image.new((sz,sz))        
        self.canvas = Canvas(redraw_callback=self.redraw,
                             event_callback=self.event)
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
        self.lock.wait()

    def event(self,ev):
        # just checking touch events
        if not ev['type'] in [key_codes.EButton1Up,
                              key_codes.EButton1Down,
                              key_codes.EDrag]:
            return
        # checking double click (show/hide toolbar)
        if ev['modifiers'] == key_codes.EModifierDoubleClick and \
           ev['type'] == key_codes.EButton1Down and \
           (not self.toolbar.is_inside(ev['pos'])):
            if not self.toolbar.is_visible():
                self.toolbar.show()
            else:
                self.toolbar.hide()
            return
        # filtering drag event before moving (we need at least
        # five consecutive drag events to move
        if ev['type'] == key_codes.EDrag and self.toolbar.is_visible():
            if self.toolbar.is_inside(ev['pos']):
                self.drag_filter_cnt = 1
            elif self.drag_filter_cnt >= 1:
                self.drag_filter_cnt += 1
            else:
                self.drag_filter_cnt = 0
            if self.drag_filter_cnt >= 5:
                self.toolbar.move(ev['pos'])
            return
        else:
            self.drag_filter_cnt = 0
        # touch UI selection             
        if ev['type'] == key_codes.EButton1Down and \
           self.toolbar.is_inside(ev['pos']) and \
           self.toolbar.is_visible():
            self.toolbar.set_sel(ev['pos'])

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
        imgs_file = [ u"e:\\python\\refresh44.png",
                      u"e:\\python\\day44.png",
                      u"e:\\python\\week44.png",
                      u"e:\\python\\month44.png",
                      u"e:\\python\\setup44.png" ]

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
        note(u"Type twice in canvas to show/hide the toolbar","info")

    def about(self):
        note(u"Canvas toolbar demo by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def close_app(self):
        self.lock.signal()
        app.set_exit()

ToolbarDemo()
