# -*- coding: utf-8 -*-
import sys
import e32
from appuifw import *
import key_codes
sys.path.append("e:\\python")
from filesel import FileSel

class EditPost:
    def __init__(self, cbk, title=u"",
                 contents=u"",
                 blog_categories = [u"Uncategorized"],                 
                 categories = [u"Uncategorized"],
                 images = [u"<empty>"]):

        self.cbk = cbk
        app.exit_key_handler = self.cancel_app
        app.title = u"Wordmobi Post"
        self.cancel = False
        self.blog_categories = blog_categories
        self.images = images
        self.categories = categories
        self.bodies = [ Text(),
                        Text(),
                        Listbox( self.images, self.popup_img ),
                        Listbox( self.categories, self.popup_cat ) ]
        self.bodies[0].style = STYLE_BOLD
        self.bodies[0].set( title )
        self.bodies[1].set( contents )
        self.bodies[0].bind(key_codes.EKeySelect, lambda: self.change_focus(0))
        self.bodies[1].bind(key_codes.EKeySelect, lambda: self.change_focus(1))

        def_menu = [( u"Publish", self.close_app ),
                    ( u"Cancel", self.cancel_app )]
        
        img_menu = [( u"Insert", self.insert_img ),
                    ( u"Remove", self.remove_img )]

        cat_menu = [( u"Select", self.select_cat )]
        
        self.menus = [ def_menu, def_menu, img_menu + def_menu, cat_menu + def_menu ]
        app.set_tabs( [ u"Title", u"Contents", u"Images", u"Categories"], self.handle_tabs )

    def change_focus(self,idx):
        if self.bodies[idx].focus == False:
            self.bodies[idx].focus = True
            app.set_tabs( [], None )
        else:
            self.bodies[idx].focus = False
            app.set_tabs( [ u"Title", u"Contents", u"Images", u"Categories"], self.handle_tabs )
            self.handle_tabs(idx)
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            if self.images[0] == u"<empty>":
                self.images = []
            self.cbk( (self.bodies[0].get(), self.bodies[1].get(), self.images, self.categories ) )
        else:
            self.cbk( (None,None,None,None) )

    def popup_img(self):
        idx = popup_menu( [u"Insert", u"Remove"], u"Images")
        if idx is not None:
            [self.insert_img , self.remove_img ][idx]()
            
    def popup_cat(self):
        idx = popup_menu( [u"Select"], u"Categories" )
        if idx is not None:
            self.select_cat()

    def insert_img(self):
        sel = FileSel().run()
        if sel is not None:
            if self.images[0] == u"<empty>":
                self.images = []
            self.images.append( sel )
            app.body.set_list( self.images )

    def remove_img(self):
        idx = app.body.current()
        self.images = self.images[:idx] + self.images[idx+1:]
        if len(self.images) == 0:
            self.images.append(u"<empty>")
        app.body.set_list( self.images )

    def select_cat(self):
        sel = multi_selection_list( self.blog_categories, style='checkbox', search_field=1 )
        if len(sel) == 0:
            self.categories = [u"Uncategorized"]
        else:
            self.categories = [ self.blog_categories[idx] for idx in sel ]
        app.body.set_list( self.categories )

    def handle_tabs(self,index):
        app.activate_tab(index)
        app.menu = self.menus[index]
        app.body = self.bodies[index]
        
    def run(self):
        self.handle_tabs(0)

if __name__ == "__main__":

    cat = [u"Uncategorized", u"Cat A", u"Cat B", u"Cat C", u"Cat D", u"Cat E"]
    ep = EditPost(u"Title",u"Post contents",cat)
    print ep.run()
