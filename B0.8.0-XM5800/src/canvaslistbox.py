# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL3

from appuifw import *
import e32
import sysinfo
import os
import graphics
import key_codes
from math import ceil, floor
#import time

__all__ = [ "_Listbox" ]
 
class CanvasListBox(Canvas):
    """ This classes creates a listbox with variable row size on canvas.
    """
    def __init__(self,**attrs):
        """ Creates a list box on canvas. Just fill the desired parameters attributes.
        """
        self.attrs = {}
        Canvas.__init__(self,
                        redraw_callback = self.redraw_list,
                        event_callback = self.event_list,
                        resize_callback = self.resize_list)
        #self.last_click = time.time()
        self.check_default_values(attrs)
        self.set_binds(True)

    def set_binds(self,enable):
        """ Enable or disable bindings
        """
        if enable:
            # TODO: use absolute coords
            ym = self.scrbar_ya + (self.scrbar_yb - self.scrbar_ya)/2
            sela=(self.lstbox_xa,self.lstbox_ya)
            selb=(self.lstbox_xb,self.lstbox_yb)
            self.bind(key_codes.EButton1Down,self.up_key,((self.scrbar_xa,self.scrbar_ya),
                                                          (self.scrbar_xb,ym)))
            self.bind(key_codes.EButton1Down, self.down_key,((self.scrbar_xa,ym),
                                                             (self.scrbar_xb,self.scrbar_yb)))
            self.bind(key_codes.EButton1Down, self.sel_key,(sela,selb))
        else:
            self.bind(key_codes.EButton1Down, None)

    def get_config(self):
        """ Return listbox attributes
        """
        return self.attrs
    
    def check_default_values(self,attrs):
        """ Given some user attributes, define all listbox attributes
        """
        if not hasattr(self,"_canvas"):
            return # canvas was not created yet !
        self.attrs = {}
        self.def_attrs = {'items':[],
                          'cbk':lambda:None,
                          'position':'auto',
                          'scrollbar_width':20,
                          'margins':(2,2,2,2),
                          'font_name':'dense',
                          'font_size':22,
                          'font_name_header':'dense',
                          'font_size_header':28,
                          'font_color':(255,255,255),
                          'font_fill_color':(0,0,0),
                          'line_space': 0,
                          'line_break_chars':u" .;:\\/-",
                          'scrollbar_color':(255,255,255),
                          'selection_font_color':(255,255,102),
                          'selection_fill_color':(124,104,238),
                          'selection_border_color':(255,255,102),
                          'odd_fill_color':(0,0,0),
                          'even_fill_color':(50,50,50),
                          'images':[],
                          'image_size':(44,44),
                          'image_keep_aspect':1,
                          'image_margin':0,
                          'title':u"",
                          'title_font':'dense',
                          'title_font_color':(255,255,102),
                          'title_fill_color':(124,104,238),
                          'title_border_color':(124,104,238)}
        
        for k in self.def_attrs.keys():
            if attrs.has_key(k):
                self.attrs[k] = attrs[k]
            else:
                self.attrs[k] = self.def_attrs[k]

        if self.attrs['position'] == "auto":
            self.attrs['position'] = (0,0,self.size[0],self.size[1])
            
        # fixing spacing
        f=(self.attrs['font_name'],self.attrs['font_size'],graphics.FONT_ANTIALIAS)
        fh = -(graphics.Image.new((1,1)).measure_text(u"[qg_|^y",font=f)[0][1])
        self.attrs['font_height'] = fh
        
        f=(self.attrs['font_name_header'],self.attrs['font_size_header'],graphics.FONT_ANTIALIAS)
        fh = -(graphics.Image.new((1,1)).measure_text(u"[qg_|^y",font=f)[0][1])
        self.attrs['font_height_header'] = fh
        self.attrs['line_space'] = max(3,fh/2,self.attrs['line_space'])
        
        # translating to origin (0,0)
        self.position = (0,
                         0,
                         self.attrs['position'][2] - self.attrs['position'][0],
                         self.attrs['position'][3] - self.attrs['position'][1])
        
        # no images, no border
        if not self.attrs['images']:
            self.attrs['image_size'] = (0,0)
            
        # if we have a title, add additional space for it
        if self.attrs['title']:
            self.attrs['title_position']=(0,
                                          0,
                                          self.position[2],
                                          self.attrs['font_height']+2*self.attrs['line_space'])
        else:
            self.attrs['title_position']=(0,0,0,0)

        # degrade effect
        self.attrs['selection_fill_light_color'] = (
            int(self.attrs['selection_fill_color'][0]*0.80) | int(255*0.20),
            int(self.attrs['selection_fill_color'][1]*0.80) | int(255*0.20),
            int(self.attrs['selection_fill_color'][2]*0.80) | int(255*0.20))
        
        # img_margin + img_size + text_margin
        self.lstbox_xa = self.position[0] + self.attrs['margins'][0] + \
                         self.attrs['image_size'][0] + self.attrs['image_margin']
        self.lstbox_ya = self.position[1] + self.attrs['margins'][1] + \
                         self.attrs['title_position'][3]
        self.lstbox_xb = self.position[2] - self.attrs['margins'][2] - \
                         self.attrs['scrollbar_width']
        self.lstbox_yb = self.position[3] - self.attrs['margins'][3]
        
        self.scrbar_xa = self.position[2] - self.attrs['scrollbar_width']
        self.scrbar_ya = self.position[1] + self.attrs['title_position'][3]
        self.scrbar_xb = self.position[2]
        self.scrbar_yb = self.position[3]

        self.images_xa = self.position[0] + self.attrs['image_margin']

        self.selbox_xa = self.position[0]
        self.selbox_xb = self.position[2] - self.attrs['scrollbar_width']

        self.lstbox_size = (self.position[2]-self.position[0],
                            self.position[3]-self.position[1])
        self._screen = graphics.Image.new(self.lstbox_size)

        #print self.attrs
        
        # selected item. It is relative to 0.
        self._current_sel = 0
        # current selection inside view. It is relative
        # to the view (self._selection_view[0]).
        self._current_sel_in_view = 0
        # current items in the view. It is relative to 0
        self._selection_view = [0,0]
        # save original data
        self._items = self.attrs['items']
        self.build_list(self.attrs['items'])        
        self.calculate_sel_view()
        self.redraw_list()
        
    def reconfigure(self,attrs={}):
        """ Given some user attributes, define e reconfigure all listbox attributes
        """        
        self.check_default_values(attrs)
        
    def redraw_list(self,rect=None):
        """ Redraw the listbox. This routine only updates the listbox area, defined
            self.attrs['position']
        """
        self.set_binds(False) # it is necessary to disable bindings since redrawing may takes a long time
        self.clear_list()
        self.draw_title()
        self.draw_scroll_bar()
        self.redraw_items()
        self.blit(self._screen,
                  target=(self.attrs['position'][0],self.attrs['position'][1]),
                  source=((0,0),self.lstbox_size))
        self.set_binds(True)

    def draw_title(self):
        """ If a title was specified, redraw it
        """
        if self.attrs['title']:
            self._screen.rectangle((self.attrs['title_position']),
                                   outline = self.attrs['title_border_color'],
                                   fill = self.attrs['title_fill_color'])  
            self._screen.text((self.attrs['title_position'][0],
                               self.attrs['title_position'][1]+
                               self.attrs['font_height']+
                               self.attrs['line_space']),
                              self.attrs['title'],
                              fill=self.attrs['title_font_color'],
                              font=self.attrs['title_font'])
            
    def draw_scroll_bar(self):
        """ Draw the scroolbar
        """
        self._screen.rectangle((self.scrbar_xa,
                                self.scrbar_ya,
                                self.scrbar_xb,
                                self.scrbar_yb),
                               outline = self.attrs['scrollbar_color'])
        list_size = len(self.lstbox_items)
        if list_size:
            pos = self.scrbar_ya + self._current_sel*(self.scrbar_yb-
                                                      self.scrbar_ya)/float(list_size)
            pos = int(pos)
            pos_ya = max(self.scrbar_ya,pos-10)
            pos_yb = min(self.scrbar_yb,pos+10)
            self._screen.rectangle((self.scrbar_xa, pos_ya, self.scrbar_xb, pos_yb),
                                   outline = self.attrs['scrollbar_color'],
                                   fill = self.attrs['scrollbar_color'])            

    def redraw_items(self):
        """ Redraw current visible listbox items
        """
        fh=(self.attrs['font_name_header'],self.attrs['font_size_header'],graphics.FONT_ANTIALIAS)
        fn=(self.attrs['font_name'],self.attrs['font_size'],graphics.FONT_ANTIALIAS)
        xa = self.lstbox_xa
        xb = self.lstbox_xb
        y = self.lstbox_ya + self.attrs['font_height']
        ysa = self.lstbox_ya
        n = self._selection_view[0]
        while y < self.lstbox_yb and n < len(self.lstbox_items):
            row = self.lstbox_items[n]
            # select fill color
            ysb = ysa + row['height']
            font_color = self.attrs['font_color']
            if n == self._current_sel:
                font_color = self.attrs['selection_font_color']
                # selection at center
                pos = (self.selbox_xa,ysa-int(ceil(self.attrs['line_space']/2)),
                       self.selbox_xb,ysb + 1 -int(floor(self.attrs['line_space']/2)))
                outline = self.attrs['selection_border_color']
                fill = self.attrs['selection_fill_color']
            elif n % 2:
                pos = (self.selbox_xa,ysa,self.selbox_xb,ysb)
                outline = self.attrs['odd_fill_color']
                fill = self.attrs['odd_fill_color']
            else:
                pos = (self.selbox_xa,ysa,self.selbox_xb,ysb)
                outline = self.attrs['even_fill_color']
                fill = self.attrs['even_fill_color']
            self._screen.rectangle(pos,outline = outline,fill = fill)
            # degrade effect for selection
            if n == self._current_sel:
                dgdc = self.attrs['selection_fill_light_color']
                dgdp = (pos[0],pos[1],pos[2],pos[3] - (pos[3]-pos[1])/2)
                self._screen.rectangle(dgdp,outline = dgdc,fill = dgdc)
            ysa = ysb
            # draw image, if any
            if row['file']:
                if not row['image']: # loading image only when necessary
                    try:
                        row['image'] = graphics.Image.open(row['file'])
                        if row['image'].size[0] > self.attrs['image_size'][0] or \
                           row['image'].size[1] > self.attrs['image_size'][1]:
                            row['image'] = row['image'].resize(self.attrs['image_size'],
                                                               keepaspect=self.attrs['image_keep_aspect'])
                    except:
                        row['image'] = graphics.Image.new(self.attrs['image_size'])
                        row['image'].clear(fill)
                        row['image'].text((1,self.attrs['image_size'][1]/2+self.attrs['font_height']/2),
                                          u"X",
                                          fill=font_color,
                                          font=fh)
                self._screen.blit(row['image'],
                                  target=(self.images_xa,y-self.attrs['font_height']-1),
                                  source=((0,0),self.attrs['image_size']))
            #draw text
            yh = 0
            self._screen.text((xa,y+yh),row['text'][0],fill=font_color,font=fh)
            yh += self.attrs['font_height_header'] + self.attrs['line_space']
            if len(row['text']) > 1:
                self._screen.text((xa,y+yh),row['text'][1],fill=font_color,font=fn)
                yh += self.attrs['font_height'] + self.attrs['line_space']

            y += row['height']
            n += 1

    def calculate_sel_view(self):
        """ Calculate the range of visible items
        """
        n = self._selection_view[0]
        y = self.lstbox_ya
        while y < self.lstbox_yb and n < len(self.lstbox_items):
            y += self.lstbox_items[n]['height']
            n += 1
        if y >= self.lstbox_yb:
            # ensure all items in view are visible
            n -= 1
        # base index is 0
        self._selection_view[1] = n - 1
            
    def up_key(self,pos):
        """ handle up navi key
        """
        if self._current_sel <= 0:
            return       
        n = self._current_sel - 1
        if n < self._selection_view[0]:
            self._selection_view[0] -= 1
            self.calculate_sel_view()
        else:
            self._current_sel_in_view -= 1
            
        self._current_sel = self._current_sel_in_view + self._selection_view[0]
        self.redraw_list()               

    def down_key(self,pos):
        """ Handle down navi key
        """
        if self._current_sel >= (len(self.lstbox_items) - 1):
            return
        n = self._current_sel + 1
        if n > self._selection_view[1]:
            # ensure that selected item in inside the view,
            # increasing the begining until it fits
            while n > self._selection_view[1]:
                self._selection_view[0] += 1
                self.calculate_sel_view()
            self._current_sel_in_view = n - self._selection_view[0]
        else:
            self._current_sel_in_view += 1

        self._current_sel = n
        self.redraw_list()            

    def sel_key(self,pos):
        sely = pos[1]
        #tmr = time.time()
        # double click strategy
        n = self._selection_view[0]
        y = self.lstbox_ya
        while y < self.lstbox_yb and n < len(self.lstbox_items) and y < sely:
            y += self.lstbox_items[n]['height']
            n += 1
        if y >= self.lstbox_yb:
            # ensure all items in view are visible
            n -= 1
        n -= 1
        last_sel = self._current_sel
        self._current_sel = n
        self.redraw_list()
        if (last_sel == n) and (sely < y):# and (tmr - self.last_click > 1):
            #print "selected", n
            self.attrs['cbk']()
        #self.last_click = tmr
       
    def build_list(self,items):
        """ Pre-process the items list, splitting it in several lines that fit
            in the current listbox size
        """
        if not self.attrs['images'] or (len(self.attrs['images']) != len(items)):
            have_images = False
        else:
            have_images = True
        self.lstbox_items = []
        width = self.lstbox_xb - self.lstbox_xa
        n=0
        for item in items:
            # text: array with all lines for the current text, already splitted
            # num_line: len of array
            # height: how much height is necessary for displaying
            #           this text including line space
            line2 = None
            if isinstance(item,list) or isinstance(item,tuple):
                line1 = item[0]
                if len(item) > 1:
                    line2 = item[1]
            else:
                line1 = item
                
            reg = {}
            reg['text'] = []
            reg['num_lines'] = 0
            reg['height'] = 0
            
            f = (self.attrs['font_name_header'],
                 self.attrs['font_size_header'],graphics.FONT_ANTIALIAS)
            splt_lines = self.split_text(line1,f,width)
            reg['text'] += splt_lines[0]
            reg['num_lines'] += 1
            reg['height'] += (self.attrs['font_height_header'] + self.attrs['line_space'])

            if line2:
                f = (self.attrs['font_name'],
                     self.attrs['font_size'],graphics.FONT_ANTIALIAS)
                splt_lines = self.split_text(line2,f,width)
                reg['text'] += splt_lines[0]
                reg['num_lines'] += 1
                reg['height'] += (self.attrs['font_height'] + self.attrs['line_space'])
            
            reg['file'] = None
            if have_images:
                if self.attrs['images'][n]:
                    reg['file'] = self.attrs['images'][n]
                    reg['image'] = None
                    reg['height'] = max(reg['height'],self.attrs['image_size'][1])
                
            self.lstbox_items.append(reg)
            n += 1
   
    def split_text(self, text, f, width):
        """ modified version of TextRenderer.chop for splitting text
            http://discussion.forum.nokia.com/forum/showthread.php?t=124666
        """
        lines = []
        text_left = text
        while len(text_left) > 0:
            bounding, to_right, fits = self.measure_text(text_left,
                                                         font=f,
                                                         maxwidth=width,
                                                         maxadvance=width)
            if fits <= 0:
                lines.append(text_left)
                break

            slice = text_left[0:fits]
            adjust = 0 # (preserve or not whitespaces at the end of the row)
        
            if len(slice) < len(text_left):
                # find the separator character closest to the right
                rindex = -1
                for sep in self.attrs['line_break_chars']:
                    idx = slice.rfind(sep)
                    if idx > rindex:
                        rindex = idx
                if rindex > 0:
                    if slice[rindex] == u' ':
                        adjust = 1
                    slice = slice[0:rindex]

            lines.append(slice)
            text_left = text_left[len(slice)+adjust:]
        
        return lines
    
    def event_list(self,ev):
        pass

    def clear_list(self):
        """ Clear screen
        """
        self._screen.clear(self.attrs['font_fill_color'])
        self.blit(self._screen,
                  target=(self.attrs['position'][0],self.attrs['position'][1]),
                  source=((0,0),self.lstbox_size))

    def current(self):
        """ Return the selected item
        """
        return self._current_sel

    def resize_list(self,rect):
        attrs = self.get_config()
        attrs['position'] = "auto"
        self.reconfigure(attrs)

class _Listbox(CanvasListBox):
    def __init__(self,items,cbk=None):
        CanvasListBox.__init__(self,items=items,cbk=cbk,position="auto")
    def set_list(self,items,def_val):
        attrs = self.get_config()
        attrs['items'] = items
        self.reconfigure(attrs)
