# -*- coding: utf-8 -*-
from appuifw import *
from window import Dialog
import wordmobi
from wmutil import *
import key_codes

__all__ = [ "Categories" ]

class Categories(Dialog):
    def __init__(self,cbk):
        self.last_idx = 0
        body = Listbox( [ u"" ], self.check_popup_menu )
        self.menu_items = [( u"Update", self.update ),
                           ( u"Delete", self.delete ),
                           ( u"Create new", self.new ) ]
        menu = self.menu_items + [( u"Close", self.close_app )]
        Dialog.__init__(self, cbk, u"Categories", body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)

    def key_left(self):
        if not self.ui_is_locked():
            self.close_app()

    def key_up(self):
        if not self.ui_is_locked():
            p = app.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Categories" % (p+1,m) )

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Categories" % (p+1,m) )
            
    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        op = popup_menu( map( lambda x: x[0], self.menu_items ) , u"Categories:")
        if op is not None:
            self.last_idx = app.body.current()
            map( lambda x: x[1], self.menu_items )[op]()

    def update(self):
        self.lock_ui(u"Downloading categories...")
        wordmobi.BLOG.update_categories()
        self.unlock_ui()

        self.refresh()

    def delete(self):
        item = app.body.current()
        cat_name = self.headlines[item]
        ny = popup_menu( [u"No", u"Yes"], u"Delete %s ?" % cat_name)
        if ny is not None:
            if ny == 1:
                self.lock_ui(u"Deleting category %s ..." % cat_name)
                wordmobi.BLOG.delete_category(item)
                self.unlock_ui()
                self.refresh()

    def new(self):
        cat_name = query(u"Category name:", "text", u"" )
        if cat_name is not None:
            self.lock_ui(u"Creating category %s ..." % cat_name)
            ret = wordmobi.BLOG.new_category( cat_name )
            self.unlock_ui()
            if ret:
                self.update()        
    
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 
        
        self.headlines = wordmobi.BLOG.categoryNamesList()
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        self.set_title( u"[%d/%d] Categories" % ( app.body.current()+1,len(self.headlines) ) )

        app.body.set_list( self.headlines, self.last_idx )
        
