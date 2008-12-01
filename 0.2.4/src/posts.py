# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32
from appuifw import *
from filesel import FileSel
import os, re
from beautifulsoup import BeautifulSoup

PARAGRAPH_SEPARATOR = u"\u2029"

class Contents(object):
    def __init__(self, cbk, contents=u""):
        self.cbk = cbk
        self.cancel = False

        self.body = Text( self.html_to_wiki(contents) )
        self.body.focus = True

        self.refresh()

    def html_to_wiki(self,msg):
        return msg.replace(u"<br>",PARAGRAPH_SEPARATOR)
    
    def wiki_to_html(self,msg):
        return msg.replace(PARAGRAPH_SEPARATOR,u"<br>")
        
    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = u"New Post"

        app.body = self.body
        app.menu = [( u"Cancel", self.cancel_app )]          

    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.cbk( self.wiki_to_html(self.body.get()) )
        else:
            self.cbk( None )

    def run(self):
        pass
            
class NewPost(object):
    def __init__(self,
                 cbk,
                 title=u"",
                 contents=u"",
                 blog_categories = [u"Uncategorized"],                 
                 categories = [],
                 images = []):
        
        self.cbk = cbk
        self.title = title
        self.contents = contents
        self.blog_categories = blog_categories
        self.categories = categories
        self.images = images
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.cancel = False
        self.last_idx = 0
        self.menu = [ ( u"Cancel", self.cancel_app ) ]
        self.app_title = u"New Post"

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = self.app_title
        
        img = unicode(",".join(self.images))
        cat = unicode(",".join(self.categories))

        self.lst_values = [ (u"Title", self.title ), \
                            (u"Contents", self.contents[:50]), \
                            (u"Categories", cat), \
                            (u"Images", img ) ]

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
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.lock_ui()
            if self.cbk( (self.title, self.contents, self.images, self.categories) ) == False:
                self.unlock_ui()
                self.refresh()
        else:
            self.cbk( (None,None,None,None) )

    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update_value( app.body.current() )

    def update_value(self,idx):
        self.last_idx = idx
        if idx == 0:
            title = query(u"Post title:","text", self.title)
            if title is not None:
                self.title = title
            self.refresh()
        elif idx == 1:
            def cbk( txt ):
                if txt is not None:
                    self.contents = txt
                self.refresh()
            self.dlg = Contents( cbk, self.contents )
            self.dlg.run()
        elif idx == 2:
            sel = multi_selection_list( self.blog_categories, style='checkbox', search_field=1 )
            if len(sel) == 0:
                self.categories = [u"Uncategorized"]
            else:
                self.categories = [ self.blog_categories[idx] for idx in sel ]
            self.refresh()            
        elif idx == 3:
            ir = popup_menu( [u"Insert", u"View", u"Remove"], u"Images")
            if ir is not None:
                if ir == 0:
                    sel = FileSel().run()
                    if sel is not None:
                        self.images.append( sel )
                else:
                    if len(self.images) > 0:
                        item = selection_list(self.images, search_field=1) 
                        if item is not None:
                            if ir == 1:
                                self.view_image( self.images[item] )
                            elif ir == 2:
                                self.images = self.images[:item] + self.images[item+1:]
                    else:
                        note(u"No images selected.","info")
            self.refresh()

    def view_image( self, img):
        if os.path.isfile( img ):
            local = True
        else:
            local = False
            
        if local:
            viewer = Content_handler( self.refresh )
            try:
                viewer.open( img )
            except:
                note(u"Impossible to open %s" % img,"error") 
        else:
            note(u"Support for remote images not implemented.","info")
            pass
            # download it to local folder with urllib and visualize
            # urllib.urlretrieve( url, local_file )
    def run(self):
        self.refresh()

class EditPost(NewPost):
    def __init__(self,
                 cbk,
                 title=u"",
                 contents=u"",
                 blog_categories = [u"Uncategorized"],                 
                 categories = [],
                 images = []):
        
        super(EditPost,self).__init__(cbk,title,contents,blog_categories,categories,images)
        self.app_title = u"Edit Post"
        self.find_images()
        
    def find_images(self):
        soup = BeautifulSoup( self.contents.encode('utf-8') )
        imgs = soup.findAll('img')
        for img in imgs:
            try:
                self.images.append( img['src'] )
            except:
                pass


    
