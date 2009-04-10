# -*- coding: utf-8 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3

from appuifw import *
import e32
import time
import sysinfo
import graphics

class SigWatch:

    BLACK = (0,0,0)
    DARK_GREEN = (0,102,0)
    BLUE1 = (51,204,255)
    YELLOW = (255,255,102)

    def __init__(self):
        self.screen = None
        self.samples = []
        self.sampling_time = 2
        self.filename = "e:\\sigwatch.txt"
        self.sampling = False        
        app.title = u"Signal Watch"
        app.screen = "full"        
        app.menu = [( u"Start", self.start ),
                    ( u"Stop", self.stop),
                    ( u"Config", self.config),
                    ( u"About", self.about ),
                    ( u"Exit", self.quit_app )]

        self.canvas = Canvas( redraw_callback = self.redraw, \
                                  event_callback = self.event )

        app.body = self.canvas
        self.timer = e32.Ao_timer()
        self.width, self.height = self.canvas.size
        self.screen = graphics.Image.new( (self.width, self.height) )
        self.screen.clear( self.BLACK )
        self.draw_grid()
        self.screen.text((5,15),u"Signal Watch - Press Start", fill = self.BLUE1)
        self.canvas.blit( self.screen )        
        app.exit_key_handler = self.quit_app        

    def quit_app(self):
        self.stop()
        self.lock.signal()

    def about(self):
        note( u"Signal Watch by\nMarcelo Barros\nmarcelobarrosalmeida@gmail.com", "info" )

    def start(self):
        self.file = open(self.filename,"wt")
        self.samples = []
        self.sampling = True
        self.timer.after(self.sampling_time,self.get_sample)
        
    def get_sample(self):
        if self.sampling:
            b = sysinfo.signal_bars()
            self.samples.insert( 0, b )
            self.file.write( "%d; %s\n" % (b,time.asctime()))
            self.file.flush()
            self.redraw( (self.width, self.height) )
            self.timer.after(self.sampling_time,self.get_sample)
        
    def stop(self):
        self.timer.cancel()
        self.sampling = False
        self.file.close()

    def draw_grid(self):
        w,h = self.width, self.height
        step = 10
        for x in range(0,w,step):
            self.screen.line( (x,0,x,h), outline = self.DARK_GREEN )
        for y in range(0,h,step):
            self.screen.line( (0,y,w,y), outline = self.DARK_GREEN )

        self.screen.line( (w-1,0,w-1,h), outline = self.DARK_GREEN )
        self.screen.line( (0,h-1,w,h-1), outline = self.DARK_GREEN )

    def draw_points(self):
        ns = len(self.samples)
        h = self.height - 1
        step = 2
        mindbm = 75;
        maxdbm = 105
        if ns >= 2:
            line_bar = []
            n = int( self.width / step )
            for i in range(ns):
                
                ybar = h  - int(h*(self.samples[i]/7.0))
                xbar = (n-i)*step
                
                if xbar < 0: # only points that fit into screen
                    break
                
                line_bar.append( (xbar, ybar) )
                
            self.draw_lines(line_bar,self.BLUE1)
            self.screen.text((5,15),u"Signal bar: %d   [0,7]" % self.samples[0], fill = self.BLUE1)

    def draw_lines(self,lines,color_name):
        for p in range(len(lines) - 1):
            coord = ( lines[p][0], lines[p][1], lines[p+1][0], lines[p+1][1] )
            self.screen.line( coord, outline = color_name )
        
    def redraw(self,rect):
        if self.screen:
            self.screen.clear( self.BLACK )
            self.draw_grid()
            self.draw_points()
            self.canvas.blit( self.screen )

    def event(self,event):
        pass

    def config(self):
        sampling = query(u"Sampling time ?", "number", self.sampling_time)
        if sampling is not None:
            self.sampling_time = max(1,sampling)
        
    def run(self):
        self.lock = e32.Ao_lock()
        self.lock.wait()
        app.set_tabs( [], None )
        app.menu = []
        app.body = None
        app.set_exit()

if __name__ == "__main__":

    sw = SigWatch()
    sw.run()
    
