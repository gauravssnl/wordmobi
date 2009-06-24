# -*- coding: utf-8 -*-
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
        (sms_id,txt,tmr,addr) = self.results[idx]
        msg = u"From: " + addr + u"\n"
        msg = msg + u"Date: " + tmr + u"\n\n"
        msg = msg + txt
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
        folders = [inbox.EInbox,inbox.EOutbox,inbox.ESent,inbox.EDraft]
        for f in folders:
            ibx = inbox.Inbox(f)
            for sms_id in ibx.sms_messages():
                txt = ibx.content(sms_id)
                print "->",txt
                txt_utf8 = txt.encode('utf-8')
                pattern_utf8 = pattern.encode('utf-8')
                if self.bmh_search(pattern_utf8.lower(),txt_utf8.lower()) > -1:
                    tmr = unicode(time.ctime(ibx.time(sms_id)),'utf-8',errors='ignore')
                    self.results.append((sms_id,txt,tmr,ibx.address(sms_id)))
                    lst.append(txt[:50])
        if self.results:
            self.body = Listbox(lst,self.lst_cbk)
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
