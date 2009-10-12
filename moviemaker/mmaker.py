# -*- coding: cp1252 -*-
# Authors:
#   Marcelo Barros de Almeida <marcelobarrosalmeida@gmail.com>
#   Marcel Pinheiro Caraciolo <caraciol@gmail.com>
# License:
#   GPL3

import graphics
import time
from appuifw import *
import os
import e32

class MMaker(object):
    NL = u"\u2029"
    def __init__(self,defdir=u"e:\mmaker",etime=0.25):
        self.dir = defdir
        self.etime = etime
        self.cnt = 0
        self.running = False
        self.timer = e32.Ao_timer()
        menu = [(u"Start", self.start),
                (u"Stop", self.stop),
                (u"Preview", self.preview),
                (u"Set dir", self.set_dir),
                (u"Set time", self.set_time),
                (u"Clean dir",self.clean_dir),
                (u"About", self.about),
                (u"Quit", self.close_app)]
        self.img = None
        self.body_canvas = None
        self.body_text = Text()
        app.screen = "normal"
        app.body = self.body_text
        app.menu = menu
        app.tile = u"MMaker"
        app.directional_pad = False
        self.lock = e32.Ao_lock()
        if not os.path.isdir(self.dir):
            self.set_dir()
        app.exit_handler = self.close_app

    def handle_redraw(self,rect):
        if self.img:
            self.body_canvas.blit(self.img)
            
    def close_app(self):
        self.running = False        
        self.timer.cancel()
        self.lock.signal()

    def run(self):
        self.lock.wait()
        app.set_tabs( [], None )
        app.menu = []
        app.body = None
        #app.set_exit()
        
    def set_dir(self):
        dir = query(u"Images dir:","text",self.dir)
        if dir is not None:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except:
                    self.body_text.add((u"Can't create %s" % dir) + self.NL)
                    return
            self.dir = dir
            self.body_text.add((u"New dir is %s" % self.dir) + self.NL)

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
                        self.body_text.add((u"%s deleted" % fp) + self.NL)
                    except:
                        self.body_text.add((u"Cant´t delete %s" % fp) + self.NL)


    def preview(self):
        if not self.running:
            movie = [ os.path.join(self.dir,f) for f in os.listdir(self.dir) ]
            movie.reverse()
            if movie:
                app.screen = "full"
                self.body_canvas = Canvas(redraw_callback=self.handle_redraw)
                app.body = self.body_canvas
                self.img = graphics.Image.new(self.body_canvas.size)
                for frame in movie:
                    self.img.clear(0x000000)
                    snap = graphics.Image.open(frame)
                    snap = snap.resize(self.body_canvas.size)
                    self.img.blit(snap)
                    self.handle_redraw(())
                    e32.ao_yield()
                note(u"Video ended.","info")
                app.screen = "normal"
                app.body = self.body_text
                self.img = None
                self.body_canvas = None
            else:
                self.body_text.add(u"No files found." + self.NL)
        else:
            self.body_text.add(u"Stop the recording first." + self.NL)
			
    def set_time(self):
        tm = query(u"Time","float",self.etime)
        if tm is not None:
            self.body_text.add((u"New time is %f" % tm) + self.NL)
            self.etime = tm

    def start(self):
        self.timer.after(self.etime,self.take_screenshot)
        self.running = True
        self.body_text.add(u"Started" + self.NL)
        
    def stop(self):
        self.running = False
        self.timer.cancel()
        self.body_text.add(u"Stopped" + self.NL)

    def take_screenshot(self):
        if self.running:
            ss = graphics.screenshot()
            name = os.path.join(self.dir,"mm%04d.png" % self.cnt)
            self.cnt += 1
            ss.save(name)
            self.body_text.add((u"Screenshot %s" % name) + self.NL)
            self.timer.after(self.etime,self.take_screenshot)

    def about(self):
        note(u"MMaker by:\n"+
             u"Marcelo Barros and\n"+
             u"Marcel Caraciolo","info")
                        
mm = MMaker()
mm.run()
