# -*- coding: utf-8 -*-
from appuifw import *
from window import Dialog
from wmutil import *
import key_codes
from wpwrapper import BLOG
from persist import DB
from wmlocale import LABELS
from wmglobals import TOUCH_ENABLED
    
__all__ = [ "Tags" ]

class Tags(Dialog):
    def __init__(self,cbk):
        self.last_idx = 0
        body = Listbox([u""], self.check_popup_menu)
        self.menu_items = [(LABELS.loc.tg_menu_updt, self.update)]
        menu = self.menu_items + [(LABELS.loc.tg_menu_clos, self.close_app)]
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_tags, body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)

    def key_left(self):
        if not self.ui_is_locked():
            self.close_app()

    def key_up(self):
        if not self.ui_is_locked():
            p = self.body.current() - 1
            m = len(self.headlines)
            if p < 0:
                p = m - 1
            self.set_title(LABELS.loc.tg_info_tag_pos % (p+1,m))

    def key_down(self):
        if not self.ui_is_locked():
            p = self.body.current() + 1
            m = len(self.headlines)
            if p >= m:
                p = 0
            self.set_title(LABELS.loc.tg_info_tag_pos % (p+1,m))
            
    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        op = popup_menu(map(lambda x: x[0], self.menu_items) , LABELS.loc.tg_pmenu_cats)
        if op is not None:
            self.last_idx = self.body.current()
            map(lambda x: x[1], self.menu_items)[op]()

    def update(self):
        self.lock_ui(LABELS.loc.tg_info_downld_tags)
        BLOG.update_tags()
        self.unlock_ui()

        self.refresh()

    def refresh(self):
        #Dialog.refresh(self) # must be called *before*        
        #self.headlines = BLOG.tag_names_list()
        Dialog.refresh(self) # must be called *before* 

        self.headlines = BLOG.tag_names_list()
        if not self.headlines:
            self.headlines = [ LABELS.loc.tg_info_udt_tags_lst ]
            
        #self.headlines = []
        #for t in BLOG.tags:
        #    line = u"%s (%s)" % (t['name'],t['count'])
        #    self.headlines.append(line)
                               
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        app.body.set_list( self.headlines, self.last_idx )

        