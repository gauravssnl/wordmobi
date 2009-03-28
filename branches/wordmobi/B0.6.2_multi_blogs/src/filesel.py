"""
Open a selection file dialog. Returns the file selected or None.
Initial path and regular expression for filtering file list may be provided.

Examples:
sel = FileSel().run()
if sel is not None:
    ...

sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
if sel is not None:
    ...

"""

import os
import e32
from appuifw import *
import re

class FileSel(object):
    def __init__(self,init_dir = "", mask = ".*"):
        self.cur_dir = unicode(init_dir)
        if not os.path.exists(self.cur_dir):
            self.cur_dir = ""
        self.mask = mask
        self.fill_items()
        
    def fill_items(self):
        if self.cur_dir == u"":
            self.items = [ unicode(d + "\\") for d in e32.drive_list() ]
        else:
            entries = [ e.decode('utf-8')
                        for e in os.listdir( self.cur_dir.encode('utf-8') ) ]
            d = self.cur_dir
            dirs  = [ e.upper() for e in entries
                      if os.path.isdir(os.path.join(d,e).encode('utf-8'))  ]
            
            files = [ e.lower() for e in entries
                      if os.path.isfile(os.path.join(d,e).encode('utf-8')) ]
            
            files = [ f for f in files
                      if re.match(self.mask,f) ]
            dirs.sort()
            files.sort()
            dirs.insert( 0, u".." )
            self.items = dirs + files
        
    def run(self):
        while True:
            item = selection_list(self.items, search_field=1)
            if item is None:
                return None
            f = self.items[item]
            d = os.path.abspath( os.path.join(self.cur_dir,f) )
            if os.path.isdir( d.encode('utf-8') ):
                if f == u".." and len(self.cur_dir) == 3:
                    self.cur_dir = u""
                else:
                    self.cur_dir = d 
                self.fill_items()
            elif os.path.isfile( d.encode('utf-8') ):
                return d
              

