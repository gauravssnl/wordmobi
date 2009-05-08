# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL 3

import sys
try:
    # http://discussion.forum.nokia.com/forum/showthread.php?p=575213
    # Try to import 'btsocket' as 'socket' - ignored on versions < 1.9.x
    sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass

from appuifw import *
import socket
import os
import e32
import struct
import time
import re

class FileSel(object):
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
            
class TxFile(object):
    """ TxFile client class
    """
    def __init__(self):
        self.lock = e32.Ao_lock()
        self.apo = None
        self.dir = ""
        self.port = 54321
        self.ip = ""
        self.new_line = u"\u2029"
        app.title = u"TX File"
        app.screen = "normal"
        app.menu = [(u"Send file", self.send_file),
                    (u"Set AP", self.set_ap),
                    (u"About", self.about),
                    (u"Exit", self.close_app)]
        self.body = Text()
        app.body = self.body
        self.lock = e32.Ao_lock()

    def close_app(self):
        self.lock.signal()

    def set_ap(self):
        """ Try to set an access point, return True or False to indicate the success.
            If True, sets self.apo to choosen access point.
        """
        apo = self.sel_access_point()
        if apo:
            self.apo = apo
            return True
        else:
            return False
            
    def send_file(self):
        """ Send a file to server
        """
        # at leat one access point is necessary
        if not self.apo:
            if not self.set_ap():
                return
            
        # use our own IP as initial guess
        self.apo.start()
        if not self.ip:
            self.ip = self.apo.ip()

        # get server address        
        ip = query(u"Server addr", "text", unicode(self.ip))
        if ip is None:
            return
        self.ip = ip     
        
        # get filename
        full_name = FileSel(init_dir=self.dir).run()
        if full_name is None:
            return

        # transmitt file
        full_name = full_name.encode('utf-8')
        self.dir = os.path.dirname(full_name)        
        base_name = os.path.basename(full_name)
        size = os.path.getsize(full_name)

        
        self.body.add(u"Connecting to %s:%d ..." % (self.ip,self.port) + self.new_line)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect((self.ip,self.port))
        except socket.error, (val,msg):
            self.body.add(u"Error %d: %s" % (val,msg) + self.new_line)
            return

        self.body.add(u"Sending %s (%d bytes)" % (base_name,size) + self.new_line)            
        f = open(full_name,"rb")
        header = "%s\n" % (base_name) + struct.pack(">L",size) + "\n"
        s.sendall(header)
        n = 0
        ta = time.time()
        while True:
            data = f.read(1024)
            if not data:
                break
            s.sendall(data)
            n += len(data)
            if n % 100 == 0: # a mark at each 100k
                self.body.add(u".")
        s.close()
        f.close()
        tb = time.time()
        self.body.add(self.new_line + u"Finished (%0.2f kbytes/s)." % ((n/1024.0)/(tb-ta)) + self.new_line)

    def sel_access_point(self):
        """ Select and set the default access point.
            Return the access point object if the selection was done or None if not
        """
        aps = socket.access_points()
        if not aps:
            note(u"No access points available","error")
            return None
        
        ap_labels = map(lambda x: x['name'], aps)
        item = popup_menu(ap_labels,u"Access points:")
        if item is None:
            return None
        
        apo = socket.access_point(aps[item]['iapid'])
        socket.set_default_access_point(apo)
        
        return apo

    def about(self):
        note(u"TX File by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def run(self):
        self.lock.wait()
        app.set_exit()
        
if __name__ == "__main__":
    app = TxFile()
    app.run()
    
