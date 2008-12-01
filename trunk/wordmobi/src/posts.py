# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32
from appuifw import *
from filesel import FileSel
import os, re
from beautifulsoup import BeautifulSoup
from wmutil import *

class Contents(object):
    
    PARAGRAPH_SEPARATOR = u"\u2029"

    
    def __init__(self, cbk, contents=u""):
        self.cbk = cbk
        self.cancel = False

        self.body = Text( self.html_to_text(contents) )
        self.body.focus = True

        self.text_snippets = {}
        # [ 0: menu name,
        #   1: menu state (False = without /, True = with /, None = no state)
        #   2: opening string
        #   3: closing string (if any)
        #   4: function for filling - state False: opening (if any)
        #   5: function for filling - state True: closing (if any)
        # ]
        self.text_snippets["BOLD"]   = { "MENU_NAME":u"Bold",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<strong>",
                                         "CLOSE_TAG":u"</strong>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["ITALIC"] = { "MENU_NAME":u"Italic",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<em>",
                                         "CLOSE_TAG":u"</em>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["QUOTE"]  = { "MENU_NAME":u"Quote",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<blockquote>",
                                         "CLOSE_TAG":u"</blockquote>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["CODE"]   = { "MENU_NAME":u"Code",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<code>",
                                         "CLOSE_TAG":u"</code>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["MORE"]   = { "MENU_NAME":u"More",
                                         "MENU_STATE":None,
                                         "OPEN_TAG":u"<!--more-->",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["IMAGE"]  = { "MENU_NAME":u"Image",
                                         "MENU_STATE":None,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_img(False),
                                         "CLOSE_FUNC":lambda: self.insert_img(True) }
        self.text_snippets["LINK"]   = { "MENU_NAME":u"Link",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_link(False),
                                         "CLOSE_FUNC":lambda: self.insert_link(True) }
        self.text_snippets["OLIST"]  = { "MENU_NAME":u"List (ordered)",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<ol>",
                                         "CLOSE_TAG":u"</ol>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["ULIST"]  = { "MENU_NAME":u"List (unordered)",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<ul>",
                                         "CLOSE_TAG":u"</ul>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["ILIST"]  = { "MENU_NAME":u"List item",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<li>",
                                         "CLOSE_TAG":u"</li>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["INS"]    = { "MENU_NAME":u"Ins",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_ins(False),
                                         "CLOSE_FUNC":lambda: self.insert_ins(True) }
        self.text_snippets["DEL"]    = { "MENU_NAME":u"Del",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_del(False),
                                         "CLOSE_FUNC":lambda: self.insert_del(True) }

        self.refresh()

    def html_to_text(self,msg):
        return msg.replace(u"<br>",Contents.PARAGRAPH_SEPARATOR)
    
    def text_to_html(self,msg):
        return msg.replace(Contents.PARAGRAPH_SEPARATOR,u"<br>")

    def refresh(self):
        def gen_label(menu):
            prefix = u""
            if self.text_snippets[menu]["MENU_STATE"] is not None:
                if self.text_snippets[menu]["MENU_STATE"]:
                    prefix = u"/"
            return (prefix + self.text_snippets[menu]["MENU_NAME"])
        def gen_ckb(menu):
            if self.text_snippets[menu]["MENU_STATE"] is None:
                if self.text_snippets[menu]["OPEN_FUNC"] is None:
                    def cbk():
                        self.body.add(self.text_snippets[menu]["OPEN_TAG"])
                        self.refresh()
                    return cbk
                else:
                    return self.text_snippets[menu]["OPEN_FUNC"]
            elif self.text_snippets[menu]["MENU_STATE"] == False:
                if self.text_snippets[menu]["OPEN_FUNC"] is None:
                    def cbk():
                        self.body.add(self.text_snippets[menu]["OPEN_TAG"])
                        self.text_snippets[menu]["MENU_STATE"] = not self.text_snippets[menu]["MENU_STATE"]
                        self.refresh()
                    return cbk
                else:
                    return self.text_snippets[menu]["OPEN_FUNC"]
            else:
                if self.text_snippets[menu]["CLOSE_FUNC"] is None:
                    def cbk():
                        self.body.add(self.text_snippets[menu]["CLOSE_TAG"])
                        self.text_snippets[menu]["MENU_STATE"] = not self.text_snippets[menu]["MENU_STATE"]
                        self.refresh()
                    return cbk
                else:
                    return self.text_snippets[menu]["CLOSE_FUNC"]                
                    
        app.menu = [(u"Text",(
                       (gen_label("BOLD"), gen_ckb("BOLD")),
                       (gen_label("ITALIC"), gen_ckb("ITALIC")),
                       (gen_label("QUOTE"), gen_ckb("QUOTE")),
                       (gen_label("CODE"), gen_ckb("CODE")),
                       (gen_label("MORE"), gen_ckb("MORE")))
                     ),
                    (u"References",(
                        (gen_label("IMAGE"), gen_ckb("IMAGE")),
                        (gen_label("LINK"), gen_ckb("LINK")))
                     ),
                    (u"List",(
                        (gen_label("OLIST"), gen_ckb("OLIST")),
                        (gen_label("ULIST"), gen_ckb("ULIST")),
                        (gen_label("ILIST"), gen_ckb("ILIST")))
                     ),                     
                    (u"Revision", (
                        (gen_label("INS"), gen_ckb("INS")),
                        (gen_label("DEL"), gen_ckb("DEL")))
                     ),
                    ( u"Cancel", self.cancel_app )]        

        app.exit_key_handler = self.close_app
        app.title = u"New Post"

        app.body = self.body
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.cbk( self.text_to_html(self.body.get()) )
        else:
            self.cbk( None )

    def insert_img(self, closing):
        txt =  u""

        ir = popup_menu( [u"Local file", u"URL"], u"Image from:")
        if ir is not None:
            if ir == 0:
                sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
                if sel is not None:
                    txt = u"<img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" />" % (sel,os.path.basename( sel ))
            else:
                url = query(u"Image URL:","text", u"http://")
                if url is not None:
                    txt = u"<img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" />" % (url,url)

        if len(txt) > 0:                    
            self.body.add( txt )
            self.refresh()

    def insert_link(self, closing):
        txt = u""
        if closing:
            txt = u"</a>"
        else:
            url = query(u"Link URL:","text", u"http://")
            if url is not None:
                txt = u"<a href=\"%s\" target=\"_blank\" />" % (url)

        if len(txt) > 0: 
            self.text_snippets["LINK"]["MENU_STATE"] = not self.text_snippets["LINK"]["MENU_STATE"]
            self.body.add( txt )
            self.refresh()

    def insert_ins(self, closing):
        txt = u""
        if closing:
            txt = u"</ins>"
        else:
            txt = u"<ins datetime=\"%s\">" % (localtime_iso8601())

        self.text_snippets["INS"]["MENU_STATE"] = not self.text_snippets["INS"]["MENU_STATE"]
        self.body.add( txt )
        self.refresh()

    def insert_del(self, closing):
        txt = u""
        if closing:
            txt = u"</del>"
        else:
            txt = u"<del datetime=\"%s\">" % (localtime_iso8601())

        self.text_snippets["DEL"]["MENU_STATE"] = not self.text_snippets["DEL"]["MENU_STATE"]
        self.body.add( txt )
        self.refresh()
                     
    def run(self):
        self.refresh()
            
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
                    self.find_images()
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
                    sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
                    if sel is not None:
                        self.images.append( sel )
                        self.contents = self.contents + \
                                        u"<br><img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" /><br>" % \
                                        (sel,os.path.basename( sel ))
                else:
                    if len(self.images) > 0:
                        item = selection_list(self.images, search_field=1) 
                        if item is not None:
                            if ir == 1:
                                self.view_image( self.images[item] )
                            elif ir == 2:
                                # TODO: remove from contents using beautiful soap
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

    def find_images(self):
        soup = BeautifulSoup( self.contents.encode('utf-8') )
        imgs = soup.findAll('img')
        self.images = []
        for img in imgs:
            try:
                self.images.append( img['src'] )
            except:
                pass
            
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


    