# -*- coding: utf-8 -*-
import e32, key_codes
from appuifw import *
from filesel import FileSel
import os, re
from beautifulsoup import BeautifulSoup
from wmutil import *
import camera, graphics
import time, urllib
from window import Dialog
import wordmobi
import key_codes
from appuifw import InfoPopup

DEFDIR = "e:\\wordmobi\\"

class TakePhoto(Dialog):
    def __init__(self):
        self.taken = False
        self.filename = ""
        body = Canvas()
        menu = [ ( u"Take a photo", self.take_photo ),( u"Cancel", self.cancel_app ) ]
        Dialog.__init__(self, lambda: True, u"Take a Photo Contents", body, menu)
        self.bind(key_codes.EKeySelect, self.take_photo)
        
    def cancel_app(self):
        self.cancel = True
        self.filename = None

    def get_options(self):
        res = None
        while res is None:
            res = popup_menu( [u"(320x240)", u"(640x480)" ], u"Resolution ?")
        self.res = ( (320,240), (640,480) )[res]
        
        flash = None
        while flash is None:
            flash = popup_menu( [u"Auto", u"None", u"Forced" ], u"Flash ?")
        self.flash = ( "auto", "none", "forced" )[flash]            
    
    def run(self):

        Dialog.refresh(self)
        self.get_options()
        
        try:
            camera.start_finder( self.redraw )
        except:
            note(u"Could not start the view finder.","error")
            return None
        
        while (not self.taken) and (not self.cancel):
            e32.ao_yield()
            
        try:
            camera.stop_finder()
        except:
            note(u"Could not stop the view finder.","error")
        
        return self.filename

    def take_photo(self):
        try:
            img = camera.take_photo( size = self.res, flash = self.flash)
            self.filename = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".jpg"
            self.filename = os.path.join(DEFDIR, "images", self.filename)
            img.save( self.filename )            
        except:
            note(u"Could not take any photo.","error")
            self.cancel_app()
            return
        
        self.taken = True
        
    def redraw(self, img):
        app.body.blit(img)

class PostContents(Dialog):
    
    PARAGRAPH_SEPARATOR = u"\u2029"

    
    def __init__(self, cbk, contents=u""):
        body = Text( self.html_to_text(contents) )
        body.focus = True
        body.set_pos( 0 )

        Dialog.__init__(self, cbk, u"Post Contents", body, [(u"Cancel", self.cancel_app)])
        
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
        self.text_snippets["SPACE"]  = { "MENU_NAME":u"Space",
                                         "MENU_STATE":None,
                                         "OPEN_TAG":u"&nbsp;",
                                         "CLOSE_TAG":u"",
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

    def html_to_text(self,msg):
        msg = msg.replace(u"<br>",PostContents.PARAGRAPH_SEPARATOR)
        msg = msg.replace(u"<br/>",PostContents.PARAGRAPH_SEPARATOR)
        return msg.replace(u"<br />",PostContents.PARAGRAPH_SEPARATOR)
    
    def text_to_html(self,msg):
        return msg.replace(PostContents.PARAGRAPH_SEPARATOR,u"<br />")

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
                    
        self.menu = [(u"Text",(
                       (gen_label("BOLD"), gen_ckb("BOLD")),
                       (gen_label("ITALIC"), gen_ckb("ITALIC")),
                       (gen_label("QUOTE"), gen_ckb("QUOTE")),
                       (gen_label("CODE"), gen_ckb("CODE")),
                       (gen_label("SPACE"), gen_ckb("SPACE")))
                       #(gen_label("MORE"), gen_ckb("MORE"))) # TODO need more tests 
                     ),
                    (u"Links/images",(
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
                    ( u"Preview", self.preview_html ),
                    ( u"Cancel", self.cancel_app )]

        Dialog.refresh(self)
        
    def cancel_app(self):
        self.cancel = True
        self.close()

    def insert_img(self, closing):
        txt =  u""

        ir = popup_menu( [u"Local file", u"Take a photo", u"URL"], u"Image from:")
        if ir is not None:
            if ir == 0:
                sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
                if sel is not None:
                    txt = u"<img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" />" % (sel,os.path.basename( sel ))
            elif ir == 1:
                sel = TakePhoto().run()
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

    def preview_html(self):

        html = self.text_to_html(self.body.get()).encode('utf-8')
        
        name = "html_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        name = os.path.join(DEFDIR, "cache", name)

        soup = BeautifulSoup( html )
        imgs = soup.findAll('img')
        for img in imgs:
            if os.path.isfile( img["src"] ):
                img["src"] = "file://localhost/" + img["src"]
                
        html = soup.prettify().replace("\n","")      

        try:
            fp = open(name,"wt")
            fp.write(r"<html><body>")
            fp.write(html)
            fp.write(r"</body></html>")
            fp.close()
        except:
            note(u"Could not generate preview file.","error")
            return
        
        viewer = Content_handler( self.refresh )
        try:
            viewer.open( name )
        except:
            note(u"Impossible to preview." ,"error")
            
class NewPost(Dialog):
    def __init__(self,
                 cbk,
                 post_title=u"",
                 contents=u"",
                 blog_categories = [u"Uncategorized"],                 
                 categories = [],
                 publish = True):
        
        self.post_title = post_title
        self.contents = contents
        self.blog_categories = blog_categories
        self.categories = categories
        self.images = []
        self.find_images()
        self.publish = publish
        self.last_idx = 0

        body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        menu = [ ( u"Cancel", self.cancel_app ) ]
        Dialog.__init__(self, cbk, u"New Post", body, menu)
        self.bind(key_codes.EKeyLeftArrow, self.close)
        
    def refresh(self):
        Dialog.refresh(self) # must be called *before*
        
        img = unicode(",".join(self.images))
        cat = unicode(",".join(self.categories))
        if self.publish:
            pub = u"Yes"
        else:
            pub = u"No (draft)"

        self.lst_values = [ (u"Title", self.post_title ), \
                            (u"Contents", self.contents[:50]), \
                            (u"Categories", cat), \
                            (u"Images", img ), \
                            (u"Publish", pub) ]

        app.body.set_list( self.lst_values, self.last_idx )   
        
    def cancel_app(self):
        self.cancel = True
        self.close()
        
    def close(self):
        if not self.cancel:
            ny = popup_menu( [u"Yes", u"No"], u"Send post ?")
            if ny is None:
                return
            if ny == 1:
                self.cancel = True

        Dialog.close(self)
                
    def update_post_title(self):
        post_title = query(u"Post title:","text", self.post_title)
        if post_title is not None:
            self.post_title = post_title
        self.refresh()
        
    def update_contents(self):
        def cbk():
            if not self.dlg.cancel :
                self.contents = self.dlg.text_to_html( self.dlg.body.get() )
                self.find_images()
            self.refresh()
            return True
        self.dlg = PostContents( cbk, self.contents )
        self.dlg.run()

    def update_categories(self):
        sel = multi_selection_list( self.blog_categories, style='checkbox', search_field=1 )
        if len(sel) == 0:
            self.categories = [u"Uncategorized"]
        else:
            self.categories = [ self.blog_categories[idx] for idx in sel ]
        self.refresh()
        
    def update_images(self):
        ir = popup_menu( [u"Insert", u"Take a photo", u"View/List", u"Remove"], u"Images")
        if ir is not None:
            if ir == 0:
                sel = FileSel(mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
                if sel is not None:
                    self.images.append( sel )
                    self.contents = self.contents + \
                                    u"<br><img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" /><br>" % \
                                    (sel,os.path.basename( sel ))
            elif ir == 1:
                sel = TakePhoto().run()
                if sel is not None:
                    self.images.append( sel )
                    self.contents = self.contents + \
                                    u"<br><img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" /><br>" % \
                                    (sel,os.path.basename( sel ))
            else:
                if len(self.images) > 0:
                    item = selection_list(self.images, search_field=1) 
                    if item is not None:
                        if ir == 2:
                            self.view_image( self.images[item].encode('utf-8') )
                        elif ir == 3:
                            self.remove_image( self.images[item].encode('utf-8') )
                            del self.images[item]
                else:
                    note(u"No images selected.","info")
        self.refresh()

    def update_publish(self):
        self.publish = not self.publish
        self.refresh()
        
    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update( app.body.current() )
            
    def update(self,idx):
        self.last_idx = idx
        updates = ( self.update_post_title, self.update_contents, \
                    self.update_categories, self.update_images, \
                    self.update_publish )
        if idx < len(updates):
            updates[idx]()

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
            # urllib seems not to support proxy authentication
            # so, download will fail in these cases
            local_file = "img_" + time.strftime("%Y%m%d_%H%M%S", time.localtime())
            local_file = os.path.join(DEFDIR, "cache", local_file)
            d = img.rfind(".")
            if d >= 0:
                local_file = local_file + img[d:]
                self.lock_ui(u"Downloading %s" % img)
                try:
                    urllib.urlretrieve( img, local_file )
                except:
                    note(u"Impossible to download %s" % img,"error")
                    self.unlock_ui()
                    return
                self.unlock_ui()
                viewer = Content_handler( self.refresh )
                try:
                    viewer.open( local_file )
                except:
                    note(u"Impossible to open %s" % img,"error") 
            else:
                note(u"Unkown externsion for %s" % img,"error")
                
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
            
    def remove_image(self,del_img):
        soup = BeautifulSoup( self.contents.encode('utf-8') )
        imgs = soup.findAll('img')
        for img in imgs:
            if img["src"] == del_img:
                img.extract()
        self.contents = utf8_to_unicode( soup.prettify().replace("\n","") )
        
class EditPost(NewPost):
    def __init__(self, cbk, cats, post, publish ):
        NewPost.__init__(self,cbk,
                          utf8_to_unicode(post['title']),
                          utf8_to_unicode(post['description']),
                          cats,
                          [ decode_html(c) for c in post['categories'] ],
                          publish )
        self.original_state = publish
        self.set_title(u"Edit Post")
        self.post = post
        self.bind(key_codes.EKeyLeftArrow, self.cancel_app)
        self.find_images()

    def update_publish(self):
        # just allow changes if post was not published yet
        if self.original_state == False:
            NewPost.update_publish(self)
        else:
            note(u"Post already published.","info")
            
    def close(self):
        if not self.cancel:
            ny = popup_menu( [u"No", u"Yes"], u"Update post ?")
            if ny is None:
                return
            if ny == 0:
                self.cancel = True
        Dialog.close(self)
            
class Posts(Dialog):
    def __init__(self,cbk):
        self.last_idx = 0
        self.headlines = []
        self.tooltip = InfoPopup()
        body = Listbox( [ u"" ], self.check_popup_menu )
        self.menu_items = [( u"Update", self.update ),
                           ( u"View/Edit", self.contents ),
                           ( u"Delete", self.delete ),
                           ( u"List Comments", self.comments ),
                           ( u"Create new", self.new ) ]
        menu = self.menu_items + [( u"Cancel", self.cancel_app )]
        Dialog.__init__(self, cbk, u"Posts", body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.close)
        self.bind(key_codes.EKeyRightArrow, self.key_right)

    def cancel_app(self):
        self.cancel = True
        self.close()

    def key_up(self):
        if not self.ui_is_locked():
            p = app.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Posts" % (p+1,m) )
            self.tooltip.show( self.headlines[p][1], (30,30), 2000, 0.25 )

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Posts" % (p+1,m) )
            self.tooltip.show( self.headlines[p][1], (30,30), 2000, 0.25 )

    def key_right(self):
        self.contents()
        
    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        op = popup_menu( map( lambda x: x[0], self.menu_items ) , u"Posts:")
        if op is not None:
            self.last_idx = app.body.current()
            map( lambda x: x[1], self.menu_items )[op]()
    
    def comments(self):
        pass
    
    def update(self):
        self.lock_ui(u"Downloading post titles..." )
        if wordmobi.BLOG.update_posts():
            self.set_title(u"Updating categories...")
            wordmobi.BLOG.update_categories()
        self.unlock_ui()            

        if len(wordmobi.BLOG.posts) == 0:
            note( u"No posts available.", "info" )
        
        self.refresh()
    
    def delete(self):
        pass

    def new_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui()
            np = wordmobi.BLOG.upload_new_post(self.dlg.post_title,
                                               self.dlg.contents,
                                               self.dlg.categories,
                                               self.dlg.publish)
            self.unlock_ui()
            
            if np == -1:
                return False
            
        self.refresh()
        return True
    
    def new(self):
        self.dlg = NewPost( self.new_cbk, u"", u"", wordmobi.BLOG.categoryNamesList(), [], True )
        self.dlg.run()

    def contents_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui()
            ok = wordmobi.BLOG.edit_post(self.dlg.post_title,
                                         self.dlg.contents,
                                         self.dlg.categories,
                                         self.dlg.post,
                                         self.dlg.publish)
            self.unlock_ui()
            
            if not ok:
                return False
            
        self.refresh()
        return True

    def contents(self):
        idx = self.body.current()
        if len( wordmobi.BLOG.posts ) == 0:
            note( u"Please, update the post list.", "info" )
            return
        
        # if post was not totally retrieved yet, fetch all data
        if wordmobi.BLOG.posts[idx].has_key('description') == False:
            self.lock_ui(u"Downloading post...")
            ok = wordmobi.BLOG.get_post(idx)
            self.unlock_ui()
            if not ok:
                return
            
        publish = wordmobi.BLOG.posts[idx]['post_status'] == 'publish' # 'publish' or 'draft'

        self.dlg = EditPost( self.contents_cbk, wordmobi.BLOG.categoryNamesList(), wordmobi.BLOG.posts[idx], publish )
        self.dlg.run()
    
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 

        if len( wordmobi.BLOG.posts ) == 0:
            self.headlines = [ (u"<empty>", u"Please, update the post list") ]
        else:
            self.headlines = []
            for p in wordmobi.BLOG.posts:
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                line1 = u"%d/%s  %02d:%02d " % (d,MONTHS[mo-1],h,m) + utf8_to_unicode( p['title'] )[:30]
                line2 = utf8_to_unicode( p['title'] )
                self.headlines.append( ( line1 , line2 ) )
                               
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        app.body.set_list( map( lambda x: x[0], self.headlines), self.last_idx )

