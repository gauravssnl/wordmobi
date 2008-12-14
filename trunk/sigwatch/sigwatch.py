# -*- coding: utf-8 -*-
import appuifw as gui
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
        self.inbox_results = ()

    def quit_app(self):
        self.stop()
        e32.ao_sleep(2)
        self.app_lock.signal()

    def about(self):
        gui.note( u"Signal Watch\nMarcelo Barros\nmarcelobarrosalmeida@gmail.com", "info" )

    def start(self):
        self.file = open(self.filename,"wt")
        self.samples = []
        self.sampling = True
        while self.sampling:
            t = time.time()
            b = sysinfo.signal_bars()
            d = sysinfo.signal_dbm()
            self.samples.insert( 0, (t,b,d) )
            self.file.write( "%f, %d, %f\n" % (t,b,d))
            self.file.flush()
            self.redraw( (self.width, self.height) )
            e32.ao_sleep(2)
        self.file.close()
        
    def stop(self):
        self.sampling = False

    def draw_grid(self):
        w,h = self.width, self.height
        step = 10
        for x in range(0,w,step):
            self.screen.line( (x,0,x,h), outline = SigWatch.DARK_GREEN )
        for y in range(0,h,step):
            self.screen.line( (0,y,w,y), outline = SigWatch.DARK_GREEN )

        self.screen.line( (w-1,0,w-1,h), outline = SigWatch.DARK_GREEN )
        self.screen.line( (0,h-1,w,h-1), outline = SigWatch.DARK_GREEN )

    def draw_points(self):
        ns = len(self.samples)
        h = self.height - 1
        step = 2
        mindbm = 75;
        maxdbm = 105
        if ns >= 2:
            line_bar = []
            line_dbm = []
            n = int( self.width / step )
            for i in range(ns):
                
                ybar = h  - int(h*(self.samples[i][1]/7.0))
                xbar = (n-i)*step
                
                if xbar < 0: # only points that fit to screen
                    break

                ydbm = h  - int(h*(float(self.samples[i][2] - mindbm)/float(maxdbm - mindbm)))

                #print (xbar, ydbm), self.samples[i][2]
                line_bar.append( (xbar, ybar) )
                line_dbm.append( (xbar, ydbm) )
                
            self.draw_lines(line_bar,SigWatch.BLUE1)
            self.screen.text((5,15),u"Signal bar: %d   [0,7]" % self.samples[0][1], fill = SigWatch.BLUE1)

            self.draw_lines(line_dbm,SigWatch.YELLOW)
            self.screen.text((5,30),u"dBm: %d   [%d,%d]" % \
                             (self.samples[0][2],mindbm,maxdbm), fill = SigWatch.YELLOW)

             

    def draw_lines(self,lines,color_name):
        for p in range(len(lines) - 1):
            coord = ( lines[p][0], lines[p][1], lines[p+1][0], lines[p+1][1] )
            self.screen.line( coord, outline = color_name )
        
    def redraw(self,rect):
        if self.screen:
            self.screen.clear( SigWatch.BLACK )
            self.draw_grid()
            self.draw_points()
            self.canvas.blit( self.screen )

    def event(self,event):
        pass
        
    def main(self):
        self.screen = None
        self.samples = []
        self.filename = "e:\\sigwatch.txt"
        self.sampling = False        
        gui.app.title = u"Signal Watch"
        gui.app.screen = "full"        
        gui.app.menu = [( u"Start", self.start ),
                        ( u"Stop", self.stop),
                        ( u"About", self.about ),
                        ( u"Exit", self.quit_app )]

        self.canvas = gui.Canvas( redraw_callback = self.redraw, \
                                  event_callback = self.event )

        gui.app.body = self.canvas
        self.width, self.height = self.canvas.size
        self.screen = graphics.Image.new( (self.width, self.height) )
        self.screen.clear( SigWatch.BLACK )
        self.draw_grid()
        self.screen.text((5,15),u"Signal Watch - Press Start", fill = SigWatch.BLUE1)
        self.canvas.blit( self.screen )        
        gui.app.exit_key_handler = self.quit_app        
        self.app_lock = e32.Ao_lock()
        self.app_lock.wait()

if __name__ == "__main__":

    app = SigWatch()
    app.main()
