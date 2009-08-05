# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3

from appuifw import *
from appuifw import InfoPopup 
import graphics
from window import Dialog
import key_codes
import e32
import sysinfo
from wpstatsapi import *
import datetime
import os
from ctoolbar import *
import sys
from types import StringTypes
import pickle
from wmglobals import TOUCH_ENABLED,DEFDIR, RESDIR
from wpwrapper import BLOG

# TODO
# add persistency

class Stats(Dialog):
    """
    """
    MARGIN = 7
    SRD = 4 # SAMPLE_RADIUS
    SLW = 4 # SAMPLE_LINE_WIDTH
    def __init__(self,cbk):
        """
        """
        self.blog_uri = BLOG.curr_blog["blog"]
        self.api_key = BLOG.curr_blog["api_key"]
        self.proxy = BLOG.proxy
        self.max_days = 365
        self.stats = {"daily"  :{"data":[],"title":u"Blog views per day"},
                      "weekly" :{"data":[],"title":u"Blog views per week"},
                      "monthly":{"data":[],"title":u"Blog views per month"},
                      "current":"daily"}
        self.wps = WPStats(self.api_key,self.blog_uri,max_days=self.max_days,proxy=self.proxy)
        self.scr_buf = None
        self.toolbar = None
        app.screen = 'normal'
        self.body = Canvas(redraw_callback = self.stats_canvas_redraw,
                           event_callback = self.stats_event,
                           resize_callback = self.stats_resize)
        # alloc maximum size, avoiding new allocation when resizing
        sz = max(sysinfo.display_pixels())
        self.scr_buf = graphics.Image.new((sz,sz))
        if sz < 400:
            # create small graphics for tiny screens
            self.SRD = 2
            self.SLW = 2
        self.body.bind(key_codes.EKeyLeftArrow,self.key_left)
        self.body.bind(key_codes.EKeyRightArrow,self.key_right)
        self.body.bind(key_codes.EKeySelect,self.key_sel)
        self.body.bind(key_codes.EKeyUpArrow,self.key_up)
        self.body.bind(key_codes.EKeyDownArrow,self.key_down)
        self.tooltip = InfoPopup()
        self.font = ('dense',16,graphics.FONT_ANTIALIAS)
        self.set_new_data(self.stats[self.stats["current"]]["title"],
                          self.stats[self.stats["current"]]["data"])
        self.create_toolbar(sz < 400)
        self.menu = [(u"Update",self.update_stats),
                     (u"Views",(
                         (u"Daily",lambda: self.set_view('daily')),
                         (u"weekly",lambda: self.set_view('weekly')),
                         (u"Monthly",lambda: self.set_view('monthly')))),
                     (u"Exit",self.close_app)]
        Dialog.__init__(self,cbk,u"Stats",self.body,self.menu)
        Dialog.refresh(self)

    def update_stats(self):
        if self.ui_is_locked():
            return
        yn = popup_menu([u"Yes",u"No"],u"Download statistics ?")
        if yn is not None:
            if yn == 0:
                self.lock_ui(u"Downloading stats...")
                try:
                    self.stats['daily']['data'] = self.wps.get_blog_views()
                except:
                    note(u"Unable to download statistics. Please try again","info")
                else:
                    self.set_title(u"Processing...")
                    self.stats['monthly']['data'] = conv2monthly(self.stats['daily']['data'])
                    self.stats['weekly']['data'] = conv2weekly(self.stats['daily']['data'])
                    self.set_new_data(self.stats[self.stats["current"]]["title"],
                                      self.stats[self.stats["current"]]["data"])
                self.unlock_ui()
                Dialog.refresh(self)
                self.set_title(u"Stats")

    def set_view(self,view_type):
        self.stats["current"] = view_type
        self.set_new_data(self.stats[self.stats["current"]]["title"],
                          self.stats[self.stats["current"]]["data"])

    def toolbar_selected(self):
        item = self.toolbar.get_sel()
        if item == 0:
            self.update_stats()
        elif item <= 3:
            view_type = ('daily','weekly','monthly')[item-1]
            self.set_view(view_type)

    def create_toolbar(self,small_icons):
        if small_icons:
            imgs = ["refresh22.png","day22.png","week22.png","month22.png"]
        else:
            imgs = ["refresh44.png","day44.png","week44.png","month44.png"]
        self.icons = []
        for img in imgs:
            self.icons.append(graphics.Image.open(os.path.join(RESDIR,img)))
        self.toolbar = CanvasToolbar(self.scr_buf,
                                     self.toolbar_selected,
                                     self.stats_buffer_redraw,
                                     self.icons,
                                     self.top_left,
                                     (254,245,28),
                                     transparency=40)
        self.toolbar.show()

    def stats_event(self,ev):
        if not ev['type'] in [key_codes.EButton1Down,
                              key_codes.EDrag]:
            return
        if ev['type'] == key_codes.EButton1Down:
            if self.toolbar.is_inside(ev['pos']):
                self.toolbar.set_sel(ev['pos'])
            else:
                #if ev['modifiers'] == key_codes.EModifierDoubleClick:
                #    self.key_sel(ev['pos']) # update selection
                #    self.stats_resize()
                #else:
                self.key_sel(ev['pos'])
        elif ev['type'] == key_codes.EDrag and not self.toolbar.is_inside(ev['pos']):
            self.key_sel(ev['pos'])
                     
    def set_new_data(self,title,data):
        self.data = data
        self.gtitle = title
        self.gtitle_size = self.get_text_size(self.gtitle,self.font)
        self.selection = 0
        self.stats_resize()

    def key_down(self):
        self.toolbar.next()
        
    def key_up(self):
        self.toolbar.prev()
        
    def key_left(self):
        n = len(self.data)
        if n:
            self.selection = (self.selection - 1) % n
            self.stats_buffer_redraw()
            self.show_tooltip()

    def key_right(self):
        n = len(self.data)
        if n:
            self.selection = (self.selection + 1) % n
            self.stats_buffer_redraw()
            self.show_tooltip()

    def key_sel(self,pos=None):
        n = len(self.data)
        if pos and n > 0:
            # touch device, self.selection is updated only here
            x,y = pos
            p = float((x - self.top_left[0]))/(self.bot_right[0] - self.top_left[0])
            d = int(round(p*(n-1)))
            self.selection = min(max(d,0),n-1)
            self.stats_buffer_redraw()
            self.show_tooltip()
        else:
            # non touch, selecting icon in toolbar
            self.toolbar.set_sel()

    def show_tooltip(self):
        msg = u"%s\n%d views" % (self.data[self.selection][0],
                                 self.data[self.selection][1])
        self.tooltip.show(msg,(5,5),2000,0)

    def get_text_size(self,text,font):
        boundings = self.scr_buf.measure_text(text,font=font)[0]
        return (boundings[2]-boundings[0],boundings[3]-boundings[1])

    def calc_scale_limits(self):
        if self.data:
            v = map(lambda d: d[1],self.data)
            self.min_val = min(v)
            self.max_val = max(v)

    def scale(self,data_v,scr_min,scr_max,data_min,data_max):
        try:
            perc = float(data_v-data_min)/(data_max-data_min)
        except:
            # just one point, use 50% to show the point in the middle of scr
            perc = 0.5
        scr_v = perc*(scr_max-scr_min) + scr_min
        return int(scr_v)

    def calc_points(self):
        self.points = []
        num_points = len(self.data)
        for p in range(num_points):
            y = self.scale(self.data[p][1],self.bot_right[1],self.top_left[1],self.min_val,self.max_val)
            x = self.scale(p,self.top_left[0],self.bot_right[0],0,num_points-1)
            self.points.append((x,y))

    def clear_screen(self):
        self.scr_buf.clear((255,255,255))

    def draw_grid(self):
        self.scr_buf.rectangle(self.top_left+self.bot_right,width=3,
                               outline = (220,220,220))
        nx = int((self.bot_right[0]-self.top_left[0])/40)
        ny = int((self.bot_right[1]-self.top_left[1])/40)
        for n in range(nx+1):
            x = self.top_left[0]+n*40
            self.scr_buf.line((x,self.top_left[1],x,self.bot_right[1]),outline = (150,150,150),width=1)
        for n in range(ny+1):
            y = self.top_left[1]+n*40
            self.scr_buf.line((self.top_left[0],y,self.bot_right[0],y),outline = (150,150,150),width=1)
              
    def draw_points(self):
        if self.points:
            self.scr_buf.line(self.points,width=self.SLW,
                              outline = (20,86,138))
            for x,y in self.points:
                self.scr_buf.ellipse((x-self.SRD,y-self.SRD,x+self.SRD,y+self.SRD),width=self.SLW,
                                     outline = (20,86,138),
                                     fill = (255,255,255))

    def draw_title(self):
        x = (self.body.size[0] - self.gtitle_size[0])/2
        self.scr_buf.text((x,self.gtitle_size[1] + self.MARGIN/2),
                          self.gtitle,
                          fill=(20,86,138),
                          font=self.font)
        
    def draw_selection(self):
        if self.points:
            x,y = self.points[self.selection]
            self.scr_buf.ellipse((x-self.SRD,y-self.SRD,x+self.SRD,y+self.SRD),width=self.SLW,
                                 outline = (255,0,0),
                                 fill = (255,255,255))

    def draw_toolbar(self):
        if self.toolbar:
            self.toolbar.redraw()

    def refresh(self):
        Dialog.refresh(self)
        self.stats_canvas_redraw()
        
    def stats_canvas_redraw(self,rect=None):
        self.body.blit(self.scr_buf)
        
    def stats_buffer_redraw(self,rect=None):
        self.body.begin_redraw()
        self.clear_screen()
        self.draw_grid()
        self.draw_points()
        self.draw_title()
        self.draw_selection()
        self.draw_toolbar()
        self.stats_canvas_redraw()
        self.body.end_redraw()
   
    def stats_resize(self,rect=None):
        if self.scr_buf:
            # just calc if screen was already created
            self.top_left = (self.MARGIN,self.MARGIN + self.gtitle_size[1])
            self.bot_right = (self.body.size[0]-self.MARGIN,self.body.size[1]-self.MARGIN)
            self.points = []
            self.calc_scale_limits()
            self.calc_points()
            # when rotating, first redraw is called and resize is called after. Why, S60 ?
            self.stats_buffer_redraw()
   
