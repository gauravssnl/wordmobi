# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3

from appuifw import *
from appuifw import InfoPopup 
import graphics
from window import Application, Dialog
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
from wmglobals import TOUCH_ENABLED, FULL_SCR

APP_DIR = os.path.dirname(sys.modules['wpstats'].__file__)
APP_DRV = APP_DIR[0]
IMG_DIR = APP_DRV + u":\\data\\python\\wpstats\\res\\"
PRG_BIN = os.path.join(APP_DRV+u":\\data\\python\\wpstats",u"wpstats.bin")
BIN_VER = 1

class WPStatsSettings(Dialog):
    def __init__(self,cbk,
                 api_key=u"",
                 blog_uri=u"http://blogname.wordpress.com",
                 max_days=365):
        self.api_key = api_key
        self.blog_uri = blog_uri
        self.max_days = max_days
        self.last_idx = 0
        body = Listbox([(u"",u"")],self.update_value)
        menu = [( u"Cancel",self.cancel_app)]
        Dialog.__init__(self,cbk,u"Settings",body,menu)
           
    def refresh(self):
        if self.blog_uri.endswith(u"/"):
            self.blog_uri = self.blog_uri[:-1]
        values = [(u"Blog URI",self.blog_uri),
                  (u"API Key",u"*"*len(self.api_key)),
                  (u"Days",unicode(self.max_days))]
        self.body.set_list(values,self.last_idx)
        Dialog.refresh(self)
               
    def update_value(self):
        idx = self.body.current()
        self.last_idx = idx

        vars = ("blog_uri","api_key","max_days")
        labels = (u"Blog URI",u"API Key",u"Days")
        formats = ("text","text","number")
        
        val = query(labels[idx],formats[idx],self.__getattribute__(vars[idx]))
        if val is not None:
            if isinstance(val, StringTypes):
                val = val.strip()
            self.__setattr__( vars[idx],val )
            
        self.refresh()
        
class WPStatsGUI(Application):
    """
    """
    MARGIN = 7
    SRD = 4 # SAMPLE_RADIUS
    SLW = 4 # SAMPLE_LINE_WIDTH
    def __init__(self):
        """
        """
        self.update_in_progress = False
        if not self.load():
            self.api_key = u"api_key"
            self.blog_uri = u"http://blog_name.wordpress.com"
            self.max_days = 365
            self.stats = {"daily"  :{"data":[],"title":u"Blog views per day"},
                          "weekly" :{"data":[],"title":u"Blog views per week"},
                          "monthly":{"data":[],"title":u"Blog views per month"},
                          "current":"daily"}
        self.dlg = None
        self.wps = WPStats(self.api_key,self.blog_uri,max_days=self.max_days)
        self.scr_buf = None
        self.toolbar = None
        app.screen = FULL_SCR
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
        Application.__init__(self,u"WP Stats",self.body)

    def load(self):
        if os.path.exists(PRG_BIN):
            try:
                f = open(PRG_BIN,"rb")
            except:
                return False
            version = pickle.load(f)
            self.api_key = pickle.load(f)
            self.blog_uri = pickle.load(f)
            self.max_days = pickle.load(f)
            self.stats = pickle.load(f)
            return True
        else:
            return False

    def save(self):
        try:
            f = open(PRG_BIN,"wb")
        except:
            return False
        pickle.dump(BIN_VER,f)
        pickle.dump(self.api_key,f)
        pickle.dump(self.blog_uri,f)
        pickle.dump(self.max_days,f)
        pickle.dump(self.stats,f)
        f.close()
        return True
            
    def update_stats(self):
        yn = popup_menu([u"Yes",u"No"],u"Download statistics ?")
        if yn is not None:
            if yn == 0:
                self.update_in_progress = True
                try:
                    self.stats['daily']['data'] = self.wps.get_blog_views()
                except:
                    note(u"Unable to download statistics. Please try again","info")
                else:
                    self.stats['monthly']['data'] = conv2monthly(self.stats['daily']['data'])
                    self.stats['weekly']['data'] = conv2weekly(self.stats['daily']['data'])
                    self.set_new_data(self.stats[self.stats["current"]]["title"],
                                      self.stats[self.stats["current"]]["data"])
                    self.save()
                self.update_in_progress = False

    def toolbar_selected(self):
        item = self.toolbar.get_sel()
        if self.update_in_progress:
            return
        if item == 0:
            self.update_stats()
        elif item <= 3:
            self.stats["current"] = ('daily','weekly','monthly')[item-1]
            self.set_new_data(self.stats[self.stats["current"]]["title"],
                              self.stats[self.stats["current"]]["data"])
        elif item == 4:
            self.setup()
        else:
            self.close_app()
            
    def create_toolbar(self,small_icons):
        if small_icons:
            imgs = ["refresh22.png","day22.png","week22.png","month22.png","setup22.png","back22.png"]
        else:
            imgs = ["refresh44.png","day44.png","week44.png","month44.png","setup44.png","back44.png"]
        self.icons = []
        for img in imgs:
            self.icons.append(graphics.Image.open(os.path.join(IMG_DIR,img)))
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
        Application.refresh(self)
        self.stats_canvas_redraw()
        
    def stats_canvas_redraw(self,rect=None):
        self.body.blit(self.scr_buf)
        
    def stats_buffer_redraw(self,rect=None):
        self.clear_screen()
        self.draw_grid()
        self.draw_points()
        self.draw_title()
        self.draw_selection()
        self.draw_toolbar()
        self.stats_canvas_redraw()
   
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
    def setup(self):
        def cbk():
            if not self.dlg.cancel:
                self.api_key = self.dlg.api_key
                self.blog_uri = self.dlg.blog_uri
                self.max_days = self.dlg.max_days
                self.wps.reconfigure(api_key=self.api_key,
                                     blog_uri=self.blog_uri,
                                     max_days=self.max_days)
                self.save()
            self.stats_canvas_redraw()
            app.screen = FULL_SCR
            self.refresh()
        self.dlg = WPStatsSettings(cbk,self.api_key,self.blog_uri,self.max_days)
        app.screen = 'normal'
        self.dlg.run()
        
if __name__ == "__main__":
    app = WPStatsGUI()
    app.run()
    
