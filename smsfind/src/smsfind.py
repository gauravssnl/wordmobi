# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
# License: GPL 3

from window import *
from appuifw import *
import inbox
import time

class ShowSMS(Dialog):
    def __init__(self,cbk,title,msg):
        Dialog.__init__(self,cbk,title,Text(msg))
        
class SMSFind(Application):
    def __init__(self):
        self.dlg = None
        self.results = [u""]
        self.terms = u""
        body = Canvas()
        menu = [(u"Find", self.get_pattern),
                (u"About", self.about),
                (u"Exit", self.close_app)]
        Application.__init__(self,u"SMS Find",body,menu)

    def about(self):
        note( u"SMS Find.\nMarcelo Barros de Almeida\nmarcelobarrosalmeida@gmail.com", "info" )

    def lst_cbk(self):
        idx = self.body.current()
        (sms_id,txt,tmr,addr,fn) = self.results[idx]
        msg = u"Address: " + addr + \
              u"\nDate: " + tmr + \
              u"\nBox: " + fn + \
              u"\n\n" + txt
        self.dlg = ShowSMS(lambda:self.refresh(),unicode(sms_id),msg)
        self.dlg.run()
        
    def bmh_search(self, pattern, text):
        # http://code.activestate.com/recipes/117223/
        m = len(pattern)
        n = len(text)
        if m > n: return -1
        skip = []
        for k in range(256): skip.append(m)
        for k in range(m - 1): skip[ord(pattern[k])] = m - k - 1
        skip = tuple(skip)
        k = m - 1
        while k < n:
            j = m - 1; i = k
            while j >= 0 and text[i] == pattern[j]:
                j -= 1; i -= 1
            if j == -1: return i + 1
            k += skip[ord(text[k])]
        return -1
        
    def find(self,pattern):
        self.results = []
        lst = []
        folders = {inbox.EInbox:u"Inbox",
                   inbox.EOutbox:u"Outbox",
                   inbox.ESent:u"Sent",
                   inbox.EDraft:u"Draft"}
        for f,fn in folders.iteritems():
            ibx = inbox.Inbox(f)
            for sms_id in ibx.sms_messages():
                txt = ibx.content(sms_id)
                txt_utf8 = txt.encode('utf-8')
                pattern_utf8 = pattern.encode('utf-8')
                if self.bmh_search(pattern_utf8.lower(),txt_utf8.lower()) > -1:
                    tm = ibx.time(sms_id)
                    dt = unicode(time.ctime(tm),'utf-8',errors='ignore')
                    self.results.append((sms_id,txt,dt,ibx.address(sms_id),fn))
                    lst.append((tm,dt,txt[:50]))
        if self.results:
            # order following unix time and remove it after
            lst.sort(reverse=True)
            lst = map(lambda x: x[1:],lst)
            self.body = Listbox(lst,self.lst_cbk)
            app.screen = 'normal' # avoid wrong screen redraw
            self.refresh()
        else:
            note(u"No results for " + self.terms,"info")
            
    def get_pattern(self):
        pattern = query(u"Search terms:", "text", self.terms)
        if pattern is not None:
            if pattern:
                pattern = pattern.strip()
                self.terms = pattern
                self.find(pattern)  

if __name__ == "__main__":
    sms = SMSFind()
    sms.run()
