# -*- coding: utf-8 -*-
from appuifw import *
import e32
import inbox
import time

class SMSFind:

    def __init__(self):
        self.inbox_results = []
        app.exit_key_handler = self.close
        app.title = u"SMS Find"
        app.menu = [(u"Find", self.get_pattern),
                    (u"About", self.about),
                    (u"Exit", self.close)]
        app.body = Canvas()
        self.app_lock = e32.Ao_lock()
        self.app_lock.wait()

    def close(self):
        self.app_lock.signal()

    def about(self):
        note( u"SMS Find.\nMarcelo Barros\nmarcelobarrosalmeida@gmail.com", "info" )

    def lst_cbk(self):
        idx = app.body.current()
        (sms_id, txt, tmr, addr) = self.inbox_results[idx]
        msg = u"From: " + addr + u"\n"
        msg = msg + u"Date: " + tmr + u"\n"
        msg = msg + txt
        note( msg, "info" )
        
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
        self.inbox_results = []
        lst = []
        ibx = inbox.Inbox(inbox.EInbox)
        for sms_id in ibx.sms_messages():
            txt = ibx.content(sms_id)
            if self.bmh_search(pattern.lower(),txt.lower()) > -1:
                tmr = unicode(time.ctime(ibx.time(sms_id)),'utf-8',errors='ignore')
                self.inbox_results.append((sms_id, txt, tmr,ibx.address(sms_id)))
                lst.append(txt[:50])
        if self.inbox_results:
            app.body = Listbox(lst,self.lst_cbk)
            
    def get_pattern(self):
        pattern = query(u"Find what?", "text")
        if pattern is not None:
            if pattern:
                pattern = pattern.strip()
                self.find(pattern)  

if __name__ == "__main__":
    sms = SMSFind()
