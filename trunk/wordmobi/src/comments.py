# -*- coding: utf-8 -*-
import e32
from appuifw import *
from wmutil import *

class ViewComments(object):
    def __init__(self,
                 cbk,
                 comments,
                 app_title=u"View comments"):
        
        self.cbk = cbk
        self.comments = comments
        self.app_title = app_title        
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.last_idx = 0
        self.menu = [ ( u"Close", self.close_app ) ]

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = self.app_title

        self.lst_values = []
        for comment in self.comments:
            (y, mo, d, h, m, s) = parse_iso8601( comment['date_created_gmt'].value )
            if comment['status'] == 'approve':
                status = 'Approved'
            else:
                status = 'Wait. moder.'
            line1 = u"%d/%s %02d:%02d %s (%s(" % (d,MONTHS[mo-1],h,m,status,utf8_to_unicode( comment['author'] ))
            line2 = utf8_to_unicode(comment['content'])
            self.lst_values.append( (line1, line2) )

        app.body = self.body
        app.body.set_list( self.lst_values, self.last_idx )
        app.menu = self.menu        

    def lock_ui(self,msg = u""):
        self.ui_lock = True
        app.menu = []
        if msg:
            app.title = msg

    def unlock_ui(self):
        self.ui_lock = False
        app.menu = self.menu
        app.title = self.title

    def ui_is_locked(self):
        return self.ui_lock
        
    def close_app(self):
        self.cbk()

    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update_value( app.body.current() )

    def update_value(self,idx):
        self.last_idx = idx
        note(u"Details are coming soon !","info")
        #self.refresh()
        
    def run(self):
        self.refresh()
