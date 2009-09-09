# -*- coding: utf-8 -*-
from appuifw import *
from window import Dialog
from wmutil import *
import key_codes
from wpwrapper import BLOG
from persist import DB
from wmlocale import LABELS

__all__ = [ "Categories" ]

class Categories(Dialog):
    def __init__(self,cbk):
        self.last_idx = 0
        body = Listbox( [ u"" ], self.check_popup_menu )
        self.menu_items = [( LABELS.loc.ca_menu_updt, self.update ),
                           ( LABELS.loc.ca_menu_dele, self.delete ),
                           ( LABELS.loc.ca_menu_cnew, self.new ) ]
        menu = self.menu_items + [( LABELS.loc.ca_menu_clos, self.close_app )]
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_cats, body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)

    def key_left(self):
        if not self.ui_is_locked():
            self.close_app()

    def key_up(self):
        if not self.ui_is_locked():
            p = self.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( LABELS.loc.ca_info_cat_pos % (p+1,m) )

    def key_down(self):
        if not self.ui_is_locked():
            p = self.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( LABELS.loc.ca_info_cat_pos % (p+1,m) )
            
    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        op = popup_menu( map( lambda x: x[0], self.menu_items ) , LABELS.loc.ca_pmenu_cats)
        if op is not None:
            self.last_idx = self.body.current()
            map( lambda x: x[1], self.menu_items )[op]()

    def update(self):
        self.lock_ui(LABELS.loc.ca_info_downld_cats)
        BLOG.update_categories()
        self.unlock_ui()

        self.refresh()

    def delete(self):
        item = self.body.current()
        cat_name = self.headlines[item]
        ny = popup_menu([LABELS.loc.gm_no, LABELS.loc.gm_yes], LABELS.loc.ca_pmenu_delete % cat_name)
        if ny is not None:
            if ny == 1:
                self.lock_ui(LABELS.loc.ca_info_del_cat % cat_name)
                BLOG.delete_category(item)
                self.unlock_ui()
                self.refresh()

    def new(self):
        cat_name = query(LABELS.loc.ca_query_cat_name, "text", u"" )
        if cat_name is not None:
            self.lock_ui(LABELS.loc.ca_info_create_cat % cat_name)
            ret = BLOG.new_category( cat_name )
            self.unlock_ui()
            if ret:
                self.update()
            self.refresh()
    
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 
        
        self.headlines = BLOG.category_names_list()
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        self.set_title( LABELS.loc.ca_info_cat_pos % ( self.body.current()+1,len(self.headlines) ) )

        self.body.set_list( self.headlines, self.last_idx )
        
