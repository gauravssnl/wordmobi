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

class RxFile(object):
    """ RxFile server class
    """
    def __init__(self):
        self.lock = e32.Ao_lock()
        self.dir = "e:\\rxfile"
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        self.apo = None
        self.port = 54321            
        self.new_line = u"\u2029"
        app.title = u"RX File"
        app.screen = "normal"
        app.menu = [(u"About", self.about)]
        self.body = Text()
        app.body = self.body
        self.lock = e32.Ao_lock()

    def recv_file(self,cs,addr):
        """ Given a client socket (cs), receive a new file
            and save it at self.dir
        """
        data = ""
        name = ""
        size = 0
        # waiting for file name
        while True:
            n = data.find("\n")
            if n >= 0:
                name = data[:n]
                data = data[n+1:] 
                break
            try:
                buf = cs.recv(1024)
            except socket.error:
                cs.close()
                return
            data = data + buf
            
        # waiting for file size (may be useful for limits checking)
        while True:
            n = data.find("\n")
            if n >= 0:
                # unpack one long (L) using big endian (>) endianness
                size = struct.unpack(">L",data[:n])[0]
                data = data[n+1:] 
                break
            try:
                buf = cs.recv(1024)
            except socket.error:
                cs.close()
                return
            data = data + buf

        self.body.add(u"Receiving %s (%d bytes)" % (name,size) + self.new_line)            
        # waiting for file contents
        fname = os.path.join(self.dir,name)
        f = open(fname,"wb")
        n = len(data)
        while True:
            f.write(data)
            n += len(data)
            if n % 100 == 0: # a mark at each 100k
                self.body.add(u".")
            try:
                data = cs.recv(1024)
            except socket.error:
                cs.close()
                return
            if not data:
                break
        self.body.add(self.new_line + u"Finished." + self.new_line)
        cs.close()
        f.close()

    def server(self,ip,port):
        """ Starts a mono thread server at ip, port
        """
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        try:
            s.bind((ip,port))
        except socket.error, (val,msg):
            note(u"Error %d: %s" % (val,msg),"info")
            return
        
        s.listen(1)

        while True:
            (cs,addr) = s.accept()
            self.body.add(u"Connect to %s:%d" % (addr[0],addr[1]) + self.new_line)
            self.recv_file(cs,addr)

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
        note(u"RX File by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def run(self):
        self.apo = self.sel_access_point()
        if self.apo:
            self.apo.start()
            self.body.add(u"Starting server." + self.new_line)
            self.body.add(u"IP = %s" % self.apo.ip() + self.new_line)
            self.body.add(u"Port = %d" % self.port + self.new_line)
            self.body.add(u"Repository = %s" % (self.dir) + self.new_line)
            self.server(self.apo.ip(),self.port)
            self.lock.wait()
        app.set_exit()
        
if __name__ == "__main__":
    app = RxFile()
    app.run()
    
