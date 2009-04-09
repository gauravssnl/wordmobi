# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3

import graphics
import time
from appuifw import *
from window import Application
import os
import e32

class MovieMaker(Application):
    NL = u"\u2029"
    def __init__(self,dir=u"e:\moviemaker",etime=0.25):
        app.screen = "normal"
        self.dir = dir
        self.etime = etime
        self.cnt = 0
        self.running = False
        self.timer = e32.Ao_timer()
        menu = [(u"Start", self.start),
                (u"Stop", self.stop),
                (u"Set dir", self.set_dir),
                (u"Set time", self.set_time),
                (u"Clean dir",self.clean_dir),
                (u"About", self.about),
                (u"Quit", self.close_app)]        
        self.body = Text()
        Application.__init__(self,
                             u"Movie maker",
                             self.body,
                             menu)
        
    def close_app(self):
        self.running = False        
        self.timer.cancel()
        Application.close_app(self)
        
    def set_dir(self):
        dir = query(u"Images dir:","text",self.dir)
        if dir is not None:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except:
                    self.body.add((u"Can't create %s" % dir) + self.NL)
                    return
            self.dir = dir

    def clean_dir(self):
        yn = popup_menu([u"No",u"Yes"],u"Clean %s?" % self.dir)
        if yn is not None:
            if yn == 1:
                self.cnt = 0
                files = os.listdir(self.dir)
                for f in files:
                    fp = os.path.join(self.dir,f)
                    try:
                        os.remove(fp)
                        self.body.add((u"%s deleted" % fp) + self.NL)
                    except:
                        self.body.add((u"Cant´t delete %s" % fp) + self.NL)
                
    def set_time(self):
        tm = query(u"Time","float",self.etime)
        if tm is not None:
            self.body.add((u"New time is %f" % tm) + self.NL)
            self.etime = tm

    def start(self):
        self.timer.after(self.etime,self.take_screenshot)
        self.running = True
        self.body.add(u"Started" + self.NL)
        
    def stop(self):
        self.running = False
        self.timer.cancel()
        self.body.add(u"Stopped" + self.NL)

    def take_screenshot(self):
        if self.running:
            ss = graphics.screenshot()
            name = os.path.join(self.dir,"mm%04d.png" % self.cnt)
            self.cnt += 1
            ss.save(name)
            self.body.add((u"Screenshot %s" % name) + self.NL)
            self.timer.after(self.etime,self.take_screenshot)

    def about(self):
        note(u"MovieMaker by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
                        
mm = MovieMaker()
mm.run()
