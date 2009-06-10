# -*- coding: utf-8 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3
import e32
import graphics
import key_codes
from appuifw import *
import sysinfo
import time
import os

try:
    a = key_codes.EButton1Down
except:
    # adding missing key_codes just to avoid tests related
    # to touch enabled or not
    key_codes.EButton1Down=0x101
    key_codes.EButton1Up=0x102
    key_codes.EDrag=0x107
    key_codes.EModifierDoubleClick=0x00080000

O_HORIZONTAL = 1
O_VERTICAL = 2
    
class CanvasToolbar(object):
    """ Creates a toolbar given a set of square images with same size.
        Toolbar is draw as below:
        
                    img_border   margin   
                           |---|---|
            +----------------------+ --
            |                      |  | <-- margin (external margin)
            |   +--------------+   | --
            |   |              |   |  | <-- img_border (image border, for drawing selection)
            |   |   +------+   |   | --
            |   |   | ICON |   |   |
            |   |   |      |   |   |
            |   |   +------+   |   | --
            |   |              |   |  | <-- 2*img_border
            |   |              |   |  | 
            |   |   +------+   |   | --
            |   |   | ICON |   |   |
            |   |   |      |   |   |
            |   |   +------+   |   |
            |   |              |   |
            |   +--------------+   |
            |                      |
            +----------------------+         
    
    """
    # Possible orientations
    def __init__(self,canvas,sel_cbk,redraw_cbk,imgs,position=(0,0),bg=(255,255,128),
                 orientation=O_VERTICAL,transparency=0,margin=3,img_border=2):
        """ Created the toolbar object.
            Parameters:
                - canvas (Image): image buffer where toolbar will be drawn
                - sel_cbk (function): callback to be called when an icon is selected toolbar is touched
                - redraw_cbk (function): callback to be called when redrawing is necessary
                - imgs (list of Images): image list with icons
                - position ((int,int)): initial position for drawing the toolbar
                - background color ((int,int,int)): toolbar background color
                - orientation (int): O_HORIZONTAL or O_VERTICAL
                - transparency (int): transparency percentage (0 = no transparent, 100 = totally transparent)
                - margin (int): external margin
                - img_border (int): border to be added to images
        """
        self.canvas = canvas
        self.sel_cbk = sel_cbk
        self.redraw_cbk = redraw_cbk
        self.imgs = imgs
        self.position = [position[0],position[1],0,0]
        self.bcolor = bg
        self.orientation = orientation
        self.transparency = (255*(100-transparency)/100,)*3
        self.margin = margin
        self.img_border = img_border
        self.img_selected = 0
        self.selected = -1
        self.last_img_selected = -1
        self.visible = False
        self.calc_size()
        self.redraw_cbk()
        
    def calc_size(self):
        """ Using the list of images, calculate toolbar size and selection image
        """
        n = len(self.imgs)
        self.img_size = self.imgs[0].size[0]
        if self.orientation == O_HORIZONTAL:
            my = self.img_size + 2*(self.img_border + self.margin)
            mx = self.img_size*n + 2*(self.img_border*n + self.margin)
        else:
            mx = self.img_size + 2*(self.img_border + self.margin)
            my = self.img_size*n + 2*(self.img_border*n + self.margin)            
        self.size = (mx,my)
        self.position[2] = self.position[0] + mx
        self.position[3] = self.position[1] + my
        self.create_sel_img(self.img_size+2*self.img_border)
        self.tlb_img = graphics.Image.new(self.size)
        self.msk_img = graphics.Image.new(self.size,'L')
        self.msk_img.clear(self.transparency)
        
    def create_sel_img(self,sz):
        """ Creates selection image (small square with dashed border)
        """
        self.sel_img = graphics.Image.new((sz,sz))
        self.sel_img.clear(self.bcolor)
        cb = self.bcolor
        cf = (0,0,0)
        c = cb
        step = 7
        for p in range(sz):
            if p%step == 0:
                if c == cb:
                    c = cf
                else:
                    c = cb
            for b in range(self.img_border):
                self.sel_img.point((p,b),outline=c)
                self.sel_img.point((p,sz-self.img_border+b),outline=c)
                self.sel_img.point((b,p),outline=c)
                self.sel_img.point((sz-self.img_border+b,p),outline=c)
                
    def move(self,pos):
        """ Move toolbar to a new position given by pos  (int,int)
        """
        self.position = [pos[0],pos[1],pos[0]+self.size[0],pos[1]+self.size[1]]
        self.redraw_cbk()
        
    def is_visible(self):
        """ Check if toolbar is visible (True) or not (False)
        """
        return self.visible
    
    def is_inside(self,p):
        """ Checks if a given point p (int,int) is inside toolbar area or not
        """
        if p[0] > self.position[0] and \
           p[0] < self.position[2] and \
           p[1] > self.position[1] and \
           p[1] < self.position[3]:
            return True
        else:
            return False

    def redraw(self,rect=None):
        """ Redraw the toolbar
        """
        if not self.visible:
            return
        self.tlb_img.clear(self.bcolor)
        x = self.margin + self.img_border
        y = self.margin + self.img_border
        for n in range(len(self.imgs)):
            img = self.imgs[n]
            if self.img_selected == n:
                self.tlb_img.blit(self.sel_img,
                                  target=(x-self.img_border,y-self.img_border),
                                  source=((0,0),self.sel_img.size))
            self.tlb_img.blit(img,target=(x,y),source=((0,0),img.size))
            if self.orientation == O_HORIZONTAL:
                x += self.img_size + 2*self.img_border
            else:
                y += self.img_size + 2*self.img_border
        self.canvas.blit(self.tlb_img,
                         target=self.position[:2],
                         source=((0,0),self.tlb_img.size),
                         mask=self.msk_img)

    def redraw2(self,rect=None):
        """ Redraw the toolbar
        """
        if not self.visible:
            return
        self.canvas.rectangle(self.position,
                              outline = self.bcolor,
                              fill = self.bcolor)
        x = self.position[0] + self.margin + self.img_border
        y = self.position[1] + self.margin + self.img_border
        for n in range(len(self.imgs)):
            img = self.imgs[n]
            if self.img_selected == n:
                self.canvas.blit(self.sel_img,
                                 target=(x-self.img_border,y-self.img_border),
                                 source=((0,0),self.sel_img.size))
            self.canvas.blit(img,target=(x,y),source=((0,0),img.size))
            if self.orientation == O_HORIZONTAL:
                x += self.img_size + 2*self.img_border
            else:
                y += self.img_size + 2*self.img_border

    def show(self):
        """ Make the toolbar visible
        """
        if not self.visible:
            self.visible = True
            self.img_selected = 0
            self.selected = -1
            self.last_img_selected = -1
        self.redraw_cbk()
                
    def hide(self):
        """ Make the toolbar invisible
        """
        self.visible = False
        self.redraw_cbk()
            
    def next(self):
        """ Move the focus to the next icon
        """
        self.img_selected = (self.img_selected + 1)%len(self.imgs)
        self.redraw_cbk()
        
    def prev(self):
        """ Move the focus to the previous icon
        """
        self.img_selected = (self.img_selected - 1)%len(self.imgs)
        self.redraw_cbk()

    def set_sel(self,pos=None):
        """ Call this function for ensuring the selection.
            For non touch UI, the selection callback is called immediately.
            For touch UI, pos (int,int) argument is used to check if we
            have a selection (typing over an icon with focus)
            or if we are just changing the focus (typing over a new icon)
        """
        if pos:
            if self.orientation == O_HORIZONTAL:
                n = int((pos[0] - self.margin - self.position[0])/(self.img_size+2*self.img_border))
            else:
                n = int((pos[1] - self.margin - self.position[1])/(self.img_size+2*self.img_border))
            self.img_selected = min(max(n,0),len(self.imgs)-1)
            if self.img_selected == self.last_img_selected:
                self.selected = self.img_selected
                self.sel_cbk()
            else:
                self.last_img_selected = self.img_selected
            self.redraw_cbk()
        else:
            self.selected = self.img_selected
            self.sel_cbk()          
        
    def get_sel(self):
        """ Return the selected icon or -1 (no selection yet)
        """
        return self.selected


class ScribbleDemo(object):
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
        self.maintb = CanvasToolbar(self.scr_buf,
                                    self.maintb_selected,
                                    self.redraw,
                                    self.maintb_imgs,
                                    (0,0),
                                    (200,200,200),
                                    transparency=20)
        self.ticktb = CanvasToolbar(self.scr_buf,
                                    self.ticktb_selected,
                                    self.redraw,
                                    self.ticktb_imgs,
                                    (54,97),
                                    (200,200,200),
                                    orientation=O_HORIZONTAL,
                                    transparency=20)
        self.colortb = CanvasToolbar(self.scr_buf,
                                     self.colortb_selected,
                                     self.redraw,
                                     self.colortb_imgs,
                                     (54,145),
                                     (200,200,200),
                                     orientation=O_HORIZONTAL,
                                     transparency=20)
        app.body = self.canvas
        app.menu = []
        self.maintb.show()
        self.lock.wait()

    def load_imgs(self):
        d = unicode(os.getcwd()[0])
        p = d + u':\\data\\python\\'
        imgs_file = [u"new44.png",u"save44.png",u"line44.png",
                     u"color44.png",u"about44.png",u"close44.png"]
        self.maintb_imgs = []
        for fn in imgs_file:
            self.maintb_imgs.append(graphics.Image.open(p+fn))

        imgs_file = [ u"ticka44.png",u"tickb44.png",u"tickc44.png" ]
        self.ticktb_imgs = []
        for fn in imgs_file:
            self.ticktb_imgs.append(graphics.Image.open(p+fn))

        imgs_file = [ u"cblue44.png",u"cgreen44.png",u"cyellow44.png",u"cwhite44.png",u"cred44.png" ]
        self.colortb_imgs = []
        for fn in imgs_file:
            self.colortb_imgs.append(graphics.Image.open(p+fn))

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
        note(u"Scribble demo by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def close_app(self):
        self.lock.signal()
        app.set_exit()

if __name__ == '__main__':
    ScribbleDemo()
