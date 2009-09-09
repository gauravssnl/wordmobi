# -*- coding: utf-8 -*-
import os
import re
import time

import urllib
from beautifulsoup import BeautifulSoup

import e32
import key_codes
try:
    import camera
    HAS_CAM = True
except:
    HAS_CAM = False
import graphics
import key_codes
import sysinfo
from appuifw import *
from wmutil import *
from window import Dialog
from comments import Comments
import s60twitter
from urllibproxy import UrllibProxy

# "from appuifw import *" above does not working properly ... missing InfoPopup in __all__
#from appuifw import InfoPopup 

from persist import DB
from wpwrapper import BLOG
from wmglobals import DEFDIR, MGFETCH
from wmlocale import LABELS

if MGFETCH:
    import pymgfetch
    def select_file(last_dir=u''):
        return pymgfetch.browse(filetype=pymgfetch.EImageFile,title=u"Images")
else:
    from filesel import FileSel
    def select_file(last_dir=u''):
        return FileSel(init_dir=last_dir,mask = r"(.*\.jpeg|.*\.jpg|.*\.png|.*\.gif)").run()
    
__all__ = [ "NewPost", "EditPost", "Posts" ]


class TakePhoto(Dialog):
    def __init__(self):
        self.taken = False
        self.filename = ""
        # camera defines
        self.setup = {'image_size':0, 'flash_mode':0, 'exp_mode':0, 'white_mode':0  }       
        body = Canvas(redraw_callback = None)
        sz = max(body.size)
        self.scr_buf = graphics.Image.new((sz,sz))        
        menu = [ (LABELS.loc.pt_menu_pict, self.take_photo),
                 (LABELS.loc.pt_menu_res,self.img_size_menu),
                 (LABELS.loc.pt_menu_flash,self.flash_mode_menu),
                 (LABELS.loc.pt_menu_expos,self.exp_mode_menu),
                 (LABELS.loc.pt_menu_white,self.white_mode_menu),
                 (LABELS.loc.pt_menu_canc, self.cancel_app) ]
        Dialog.__init__(self, lambda: True, LABELS.loc.pt_info_pict, body, menu)
        self.bind(key_codes.EKeySelect, self.take_photo)

    def img_size_menu(self):
        img_sizes_str = [u"%dx%d" % (x[0],x[1]) for x in camera.image_sizes()]
        res = popup_menu(img_sizes_str,LABELS.loc.pt_pmenu_res)
        if res is not None:
            self.setup['image_size'] = res

    def flash_mode_menu(self):
        res = popup_menu([unicode(x) for x in camera.flash_modes()],LABELS.loc.pt_pmenu_flash)
        if res is not None:
            self.setup['flash_mode'] = res

    def exp_mode_menu(self):
        res = popup_menu([unicode(x) for x in camera.exposure_modes()],LABELS.loc.pt_pmenu_expos)
        if res is not None:
            self.setup['exp_mode'] = res

    def white_mode_menu(self):
        res = popup_menu([unicode(x) for x in camera.white_balance_modes()],LABELS.loc.pt_pmenu_white)
        if res is not None:
            self.setup['white_mode'] = res            
            
    def cancel_app(self):
        self.cancel = True
        self.filename = None
    
    def run(self):
        Dialog.refresh(self)

        try:
            camera.start_finder(self.redraw)
        except:
            note(LABELS.loc.pt_err_cant_start_viewf,"error")
            return None
        
        while (not self.taken) and (not self.cancel):
            e32.ao_yield()
            
        try:
            camera.stop_finder()
            camera.release()
        except:
            note(LABELS.loc.pt_err_cant_stop_viewf,"error")
        
        return self.filename

    def take_photo(self):
        try:
            img = camera.take_photo(size = camera.image_sizes()[self.setup['image_size']],
                                    flash = camera.flash_modes()[self.setup['flash_mode']],
                                    exposure = camera.exposure_modes()[self.setup['exp_mode']],
                                    white_balance = camera.white_balance_modes()[self.setup['white_mode']])
            self.filename = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".jpg"
            self.filename = os.path.join(DEFDIR, "images", self.filename)
            img.save(self.filename)            
        except:
            note(LABELS.loc.pt_err_cant_take_pic,"error")
            self.cancel_app()
            return
        
        self.taken = True
        
    def redraw(self, img):
        def center(a,b):
            m = int((a - b)/2)
            if m < 0: m = 0
            return m

        xm = center(app.body.size[0],img.size[0])
        ym = center(app.body.size[1],img.size[1])
        
        self.scr_buf.clear((255,255,255))
        self.scr_buf.blit(img,target=(xm,ym))
        app.body.blit(self.scr_buf)
        #app.body.clear((255,255,255))
        #app.body.blit(img,target=(xm,ym))
        app.title = unicode(camera.image_sizes()[self.setup['image_size']])

class PostContents(Dialog):
    
    PARAGRAPH_SEPARATOR = u"\u2029"
    
    def __init__(self, cbk, contents=u""):
        body = Text(self.html_to_text(contents))
        body.focus = True
        self.init_dir=""
        body.set_pos(0)

        Dialog.__init__(self, cbk, LABELS.loc.pt_info_post_contents, body,
                        [(LABELS.loc.pt_menu_canc, self.cancel_app)])
        
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
                                         "CLOSE_FUNC":None }
        self.text_snippets["LINK"]   = { "MENU_NAME":u"Link",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_link(False),
                                         "CLOSE_FUNC":lambda: self.insert_link(True) }
        self.text_snippets["LINKYT"] = { "MENU_NAME":u"Youtube Link",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_linkyt(),
                                         "CLOSE_FUNC":None }
        self.text_snippets["LINKQIK"]= { "MENU_NAME":u"Qik Link",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"",
                                         "CLOSE_TAG":u"",
                                         "OPEN_FUNC":lambda: self.insert_linkqik(),
                                         "CLOSE_FUNC":None }                
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
        self.text_snippets["H1"]     = { "MENU_NAME":u"H1",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<h1>",
                                         "CLOSE_TAG":u"</h1>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["H2"]     = { "MENU_NAME":u"H2",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<h2>",
                                         "CLOSE_TAG":u"</h2>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["H3"]     = { "MENU_NAME":u"H3",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<h3>",
                                         "CLOSE_TAG":u"</h3>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }
        self.text_snippets["H4"]     = { "MENU_NAME":u"H4",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<h4>",
                                         "CLOSE_TAG":u"</h4>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }        
        self.text_snippets["STRIKE"] = { "MENU_NAME":u"Strike",
                                         "MENU_STATE":False,
                                         "OPEN_TAG":u"<strike>",
                                         "CLOSE_TAG":u"</strike>",
                                         "OPEN_FUNC":None,
                                         "CLOSE_FUNC":None }        
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
                    
        self.global_menu = [(LABELS.loc.pt_menu_text,(
                       (gen_label("BOLD"), gen_ckb("BOLD")),
                       (gen_label("ITALIC"), gen_ckb("ITALIC")),
                       (gen_label("QUOTE"), gen_ckb("QUOTE")),
                       (gen_label("MORE"), gen_ckb("MORE")),
                       (gen_label("CODE"), gen_ckb("CODE")),
                       (gen_label("STRIKE"), gen_ckb("STRIKE")),
                       (gen_label("SPACE"), gen_ckb("SPACE")),
                       (gen_label("H1"), gen_ckb("H1")),
                       (gen_label("H2"), gen_ckb("H2")),
                       (gen_label("H3"), gen_ckb("H3")),
                       (gen_label("H4"), gen_ckb("H4")))
                      ),
                     (LABELS.loc.pt_menu_refs,(
                        (gen_label("IMAGE"), gen_ckb("IMAGE")),
                        (gen_label("LINK"), gen_ckb("LINK")),
                        (gen_label("LINKYT"), gen_ckb("LINKYT")))#,
                        #(gen_label("LINKQIK"), gen_ckb("LINKQIK")))
                      ),
                    (LABELS.loc.pt_menu_lsts,(
                        (gen_label("OLIST"), gen_ckb("OLIST")),
                        (gen_label("ULIST"), gen_ckb("ULIST")),
                        (gen_label("ILIST"), gen_ckb("ILIST")))
                     ),                     
                    (LABELS.loc.pt_menu_revs,(
                        (gen_label("INS"), gen_ckb("INS")),
                        (gen_label("DEL"), gen_ckb("DEL")))
                     ),
                     (LABELS.loc.pt_menu_prvw, self.preview_html),
                     (LABELS.loc.pt_menu_canc, self.cancel_app)]

        Dialog.refresh(self)

    def insert_img(self, closing):
        txt =  u""
        ir = popup_menu([LABELS.loc.pt_list_loc_file,
                          LABELS.loc.pt_list_take_img,
                          LABELS.loc.pt_list_url],
                         LABELS.loc.pt_pmenu_img_src)
        if ir is not None:
            if ir == 0:
                sel = select_file(self.init_dir)
                if sel is not None:
                    self.init_dir=os.path.dirname(sel)
                    ny = popup_menu([LABELS.loc.gm_no,LABELS.loc.gm_yes],
                                    LABELS.loc.pt_pmenu_scale_img)
                    scale_factor = u""
                    if ny == 1:
                        # suggested best image size: 480px
                        imgsz = graphics.Image.inspect(sel)
                        scale = (480*100)/(imgsz['size'][0])
                        scale = query(LABELS.loc.pt_pmenu_scale_factor, "number", scale)
                        if scale is not None:
                            xs = imgsz['size'][0]*scale/100
                            ys = imgsz['size'][1]*scale/100
                            scale_factor = u'width="%d" height="%d"' % (xs,ys)
                    txt = u'<a href="%s"><img border="0" class="aligncenter" src="%s" alt="%s" %s/></a>' % \
                          (sel,sel,os.path.basename(sel),scale_factor)
            elif ir == 1 and HAS_CAM:
                sel = TakePhoto().run()
                if sel is not None:
                    txt = u'<img border="0" class="aligncenter" src="%s" alt="%s" />' % (sel,os.path.basename(sel))
            else:
                url = query(LABELS.loc.pt_pmenu_img_url, "text", u"http://")
                if url is not None:
                    txt = u'<img border="0" class="aligncenter" src="%s" alt="%s" />' % (url,url)

        if txt:                    
            self.body.add(txt)

        self.refresh()

    def insert_link(self, closing):
        txt = u""
        if closing:
            txt = u"</a>"
        else:
            url = query(LABELS.loc.pt_pmenu_link_url, "text", u"http://")
            if url is not None:
                txt = u"<a href=\"%s\" target=\"_blank\" />" % (url)

        if txt: 
            self.text_snippets["LINK"]["MENU_STATE"] = not self.text_snippets["LINK"]["MENU_STATE"]
            self.body.add(txt)
            self.refresh()

    def insert_linkyt(self):
        txt = u""
        url = query(LABELS.loc.pt_pmenu_linkyt_url, "text", u"http://www.youtube.com/watch?v=")
        if url is not None:
            txt = u"[youtube=%s]" % (url)
        if txt: 
            self.body.add(txt)
            self.refresh()

    def insert_linkqik(self):
        txt = u""
        url = query(LABELS.loc.pt_pmenu_linkqik_url, "text", u"http://qik.com/video/<number>")
        if url is not None:
            txt = u"[qik url=%s]" % (url)
        if txt: 
            self.body.add(txt)
            self.refresh()
            
    def insert_ins(self, closing):
        txt = u""
        if closing:
            txt = u"</ins>"
        else:
            txt = u"<ins datetime=\"%s\">" % (localtime_iso8601())

        self.text_snippets["INS"]["MENU_STATE"] = not self.text_snippets["INS"]["MENU_STATE"]
        self.body.add(txt)
        self.refresh()

    def insert_del(self, closing):
        txt = u""
        if closing:
            txt = u"</del>"
        else:
            txt = u"<del datetime=\"%s\">" % (localtime_iso8601())

        self.text_snippets["DEL"]["MENU_STATE"] = not self.text_snippets["DEL"]["MENU_STATE"]
        self.body.add(txt)
        self.refresh()

    def preview_html(self):

        html = self.text_to_html(self.body.get()).encode('utf-8')
        
        name = "html_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        name = os.path.join(DEFDIR, "cache", name)

        soup = BeautifulSoup(html)
        imgs = soup.findAll('img')
        for img in imgs:
            if os.path.isfile(img["src"]):
                img["src"] = "file://localhost/" + img["src"]
                
        html = soup.prettify().replace("\n","")      

        try:
            fp = open(name,"wt")
            fp.write("<html>\n")
            fp.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n')
            fp.write("<body>\n")
            fp.write(html)
            fp.write("</body></html>")
            fp.close()
        except:
            note(LABELS.loc.pt_err_cant_gen_prvw,"error")
            return
        
        viewer = Content_handler(self.refresh)
        try:
            viewer.open(name)
        except:
            note(LABELS.loc.pt_err_cant_prvw,"error")
            
class NewPost(Dialog):
    def __init__(self,
                 cbk,
                 post_title=u"",
                 contents=u"",
                 blog_categories = [LABELS.loc.wp_list_uncategorized],                 
                 categories = [],
                 blog_tags = [],
                 tags = [],
                 publish = True):
        
        self.post_title = post_title
        self.contents = contents
        self.blog_categories = blog_categories
        self.categories = categories
        self.blog_tags = blog_tags
        self.tags = tags
        self.images = []
        self.find_images()
        self.publish = publish
        self.last_idx = 0
        self.save = False
        self.init_dir=""

        body = Listbox([ (u"",u"") ], self.update_value_check_lock)
        menu = [ (LABELS.loc.pt_menu_canc, self.cancel_app) ]
        Dialog.__init__(self, cbk, LABELS.loc.pt_info_new_post, body, menu)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value_check_lock)
        
    def refresh(self):
        Dialog.refresh(self) # must be called *before*
        
        imgs = unicode(",".join(self.images))
        cats = unicode(",".join(self.categories))
        tags = unicode(",".join(self.tags))
        if self.publish:
            pub = LABELS.loc.pt_info_no_pub
        else:
            pub = LABELS.loc.pt_info_draft

        lst_values = [(LABELS.loc.pt_menu_titl, self.post_title),
                      (LABELS.loc.pt_menu_cont, self.contents[:50]),
                      (LABELS.loc.pt_menu_cats, cats),
                      (LABELS.loc.pt_menu_tags, tags),
                      (LABELS.loc.pt_menu_imgs, imgs),
                      (LABELS.loc.pt_menu_pubs, pub)]

        app.body.set_list(lst_values, self.last_idx)   
                
    def update_post_title(self):
        post_title = query(LABELS.loc.pt_pmenu_post_title, "text", self.post_title)
        if post_title is not None:
            self.post_title = post_title
        self.refresh()
        
    def update_contents(self):
        def cbk():
            if not self.dlg.cancel :
                self.contents = self.dlg.text_to_html(self.dlg.body.get())
                self.find_images()
            self.refresh()
            return True
        self.dlg = PostContents(cbk, self.contents)
        self.dlg.run()

    def update_categories(self):
        op = popup_menu([LABELS.loc.pt_list_sel_cat,
                         LABELS.loc.pt_list_rem_cat,
                         LABELS.loc.pt_list_lst_cat],
                        LABELS.loc.pt_pmenu_cats)
        if op is not None:
            if op == 0:
                sel = multi_selection_list(self.blog_categories, style='checkbox', search_field=1)
                if sel is not None:
                    cats = [ self.blog_categories[idx] for idx in sel ]
                    self.categories += cats
            elif op == 1 and self.categories:
                sel = multi_selection_list(self.categories, style='checkbox', search_field=1)
                if sel is not None:
                    idxs = range(len(self.categories))
                    self.categories = [ self.categories[idx] for idx in idxs if idx not in sel ]
            elif op == 2 and self.categories:
                selection_list(self.categories,search_field=1)
                    
        self.refresh()

    def update_tags(self):
        op = popup_menu([LABELS.loc.pt_list_new_tag,
                         LABELS.loc.pt_list_sel_tag,
                         LABELS.loc.pt_list_rem_tag,
                         LABELS.loc.pt_list_lst_tag],
                         LABELS.loc.pt_pmenu_tags)
        if op is not None:
            if op == 0:
                new_tag = query(LABELS.loc.pt_pmenu_tags, "text", u"")
                if new_tag is not None:
                    self.tags.append(new_tag)
            elif op == 1 and self.blog_tags:
                sel = multi_selection_list(self.blog_tags, style='checkbox', search_field=1)
                if sel is not None:
                    new_tags = [ self.blog_tags[idx] for idx in sel ]
                    self.tags += new_tags
            elif op == 2 and self.tags:
                sel = multi_selection_list(self.tags, style='checkbox', search_field=1)
                if sel is not None:
                    idxs = range(len(self.tags))
                    self.tags = [ self.tags[idx] for idx in idxs if idx not in sel ]
            elif op == 3 and self.tags:
                selection_list(self.tags,search_field=1)                    
                
        self.refresh()
    
    def update_images(self):
        ir = popup_menu([LABELS.loc.pt_list_ins_img,
                          LABELS.loc.pt_list_take_img,
                          LABELS.loc.pt_list_view_img,
                          LABELS.loc.pt_list_rem_img],
                         LABELS.loc.pt_pmenu_images)
        if ir is not None:
            if ir == 0:
                sel = select_file(self.init_dir)
                if sel is not None:
                    self.init_dir=os.path.dirname(sel)
                    ny = popup_menu([LABELS.loc.gm_no,LABELS.loc.gm_yes],
                                    LABELS.loc.pt_pmenu_scale_img)
                    scale_factor = u""
                    if ny == 1:
                        # suggested best image size: 480px
                        imgsz = graphics.Image.inspect(sel)
                        scale = (480*100)/(imgsz['size'][0])
                        scale = query(LABELS.loc.pt_pmenu_scale_factor, "number", scale)
                        if scale is not None:
                            xs = imgsz['size'][0]*scale/100
                            ys = imgsz['size'][1]*scale/100
                            scale_factor = u'width="%d" height="%d"' % (xs,ys)
                    self.images.append(sel)                    
                    self.contents = self.contents + \
                                    u'<br><img border="0" class="aligncenter" src="%s" alt="%s" %s/><br>' % \
                                    (sel,os.path.basename(sel),scale_factor)
            elif ir == 1 and HAS_CAM:
                sel = TakePhoto().run()
                if sel is not None:
                    self.images.append(sel)
                    self.contents = self.contents + \
                                    u'<br><img border="0" class="aligncenter" src="%s" alt="%s" /><br>' % \
                                    (sel,os.path.basename(sel))
            else:
                if self.images:
                    item = selection_list(self.images, search_field=1) 
                    if item is not None:
                        if ir == 2:
                            self.view_image(self.images[item].encode('utf-8'))
                        elif ir == 3:
                            self.remove_image(self.images[item].encode('utf-8'))
                            del self.images[item]
                else:
                    note(LABELS.loc.pt_info_no_imgs_sel,"info")
        self.refresh()

    def update_publish(self):
        self.publish = not self.publish
        self.refresh()
        
    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update(app.body.current())
            
    def update(self,idx):
        self.last_idx = idx
        updates = (self.update_post_title,
                   self.update_contents,
                   self.update_categories,
                   self.update_tags,
                   self.update_images,
                   self.update_publish)
        if idx < len(updates):
            updates[idx]()

    def view_image(self, img):
        if os.path.isfile(img):
            local = True
        else:
            local = False
            
        if local:
            viewer = Content_handler(self.refresh)
            try:
                viewer.open(img)
            except:
                note(LABELS.loc.pt_err_cant_open % img,"error") 
        else:
            local_file = "img_" + time.strftime("%Y%m%d_%H%M%S", time.localtime())
            local_file = os.path.join(DEFDIR, "cache", local_file)
            d = img.rfind(".")
            if d >= 0:
                local_file = local_file + img[d:]
                self.lock_ui(LABELS.loc.pt_info_downld_img % img)
                try:
                    urlprx = UrllibProxy(BLOG.get_proxy())
                    urlprx.urlretrieve(img, local_file)
                except:
                    note(LABELS.loc.pt_err_cant_downld % img,"error")
                    self.unlock_ui()
                    return
                self.unlock_ui()
                viewer = Content_handler(self.refresh)
                try:
                    viewer.open(local_file)
                except:
                    note(LABELS.loc.pt_err_cant_open % img,"error") 
            else:
                note(LABELS.loc.pt_err_unknown_ext % img,"error")
                
    def run(self):
        self.refresh()

    def find_images(self):
        soup = BeautifulSoup(self.contents.encode('utf-8'))
        imgs = soup.findAll('img')
        self.images = []
        for img in imgs:
            try:
                self.images.append(img['src'])
            except:
                pass
            
    def remove_image(self,del_img):
        soup = BeautifulSoup(self.contents.encode('utf-8'))
        imgs = soup.findAll('img')
        for img in imgs:
            if img["src"] == del_img:
                img.extract()
        self.contents = utf8_to_unicode(soup.prettify().replace("\n",""))

    def close_app(self):
        if not self.cancel:
            yns = popup_menu([LABELS.loc.gm_yes,
                             LABELS.loc.gm_no,
                             LABELS.loc.pt_list_save_it],
                            LABELS.loc.pt_pmenu_send_post)
            if yns is None:
                return
            if yns == 1:
                self.cancel = True
                self.save = False
            elif yns == 2:
                self.cancel = True
                self.save = True
            else:
                self.cancel = False
                self.save = False

        Dialog.close_app(self)
        
class EditPost(NewPost):
    def __init__(self, cbk, blog_cats, blog_tags, post_idx, publish):
        post_cats = []
        for c in BLOG.posts[post_idx]['categories']:
            # spliting an empty string will return a vector, this is not desired
            try:
                post_cats.append(decode_html(c))
            except:
                post_cats.append(utf8_to_unicode(c))
                
        post_tags = []
        if BLOG.posts[post_idx]['mt_keywords']:
            for t in BLOG.posts[post_idx]['mt_keywords'].split(','):
                try:
                    post_tags.append(decode_html(t))
                except:
                    post_tags.append(utf8_to_unicode(t))        
        # check for more tag. The idea is to reconstruct the post with <!--more--> added
        # to the right position and to eliminate mt_text_more
        if BLOG.posts[post_idx]['mt_text_more']:
            BLOG.posts[post_idx]['description'] = BLOG.posts[post_idx]['description'] + \
                                                  "<!--more-->" + \
                                                  BLOG.posts[post_idx]['mt_text_more']
            BLOG.posts[post_idx]['mt_text_more'] = ""
            
        NewPost.__init__(self,cbk,
                         utf8_to_unicode(BLOG.posts[post_idx]['title']),
                         utf8_to_unicode(BLOG.posts[post_idx]['description']),
                         blog_cats,
                         post_cats,
                         blog_tags,
                         post_tags,
                         publish)
        
        self.set_title(LABELS.loc.pt_info_edit_post)
        self.post_idx = post_idx
        self.find_images()
            
class Posts(Dialog):
    def __init__(self,cbk):
        self.last_idx = 0
        self.headlines = []
        #self.tooltip = InfoPopup()
        body = Listbox([(u"",u"")],self.check_popup_menu)
        self.menu_items = [(LABELS.loc.pt_menu_updt, self.update),
                           (LABELS.loc.pt_menu_view, self.contents),
                           (LABELS.loc.pt_menu_cnew, self.new),
                           (LABELS.loc.pt_menu_dele, self.delete),
                           (LABELS.loc.pt_menu_lstc, self.comments)]
        if DB["twitter_enabled"] == u"True":
            self.menu_items += [(LABELS.loc.pt_menu_s2tw, self.send2twitter)]
        self.menu_items += [(LABELS.loc.pt_menu_offl_publ, self.offline_publish)]
        menu = self.menu_items + [(LABELS.loc.pt_menu_clos, self.close_app)]
        
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_post, body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)
        self.bind(key_codes.EKeyRightArrow, self.key_right)

    def key_left(self):
        if not self.ui_is_locked():
            self.close_app()
            
    def key_up(self):
        if not self.ui_is_locked():
            p = app.body.current() - 1
            m = len(self.headlines)
            if p < 0:
                p = m - 1
            self.set_title(LABELS.loc.pt_info_pst_pos % (p+1,m))
            #self.tooltip.show(self.headlines[p][1], (30,30), 2000, 0.25)

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len(self.headlines)
            if p >= m:
                p = 0
            self.set_title(LABELS.loc.pt_info_pst_pos % (p+1,m))
            #self.tooltip.show(self.headlines[p][1], (30,30), 2000, 0.25)

    def key_right(self):
        if not self.ui_is_locked():
            self.contents()
        
    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        idx = app.body.current()
        self.last_idx = idx
        menu = [(LABELS.loc.pt_menu_updt, self.update),
                (LABELS.loc.pt_menu_cnew, self.new)]
        if BLOG.posts:                
            menu += [(LABELS.loc.pt_menu_view, self.contents),
                     (LABELS.loc.pt_menu_dele, self.delete)]
            if BLOG.post_is_remote(idx):
                menu += [(LABELS.loc.pt_menu_lstc, self.comments)]
                if DB["twitter_enabled"] == u"True":
                    menu += [(LABELS.loc.pt_menu_s2tw, self.send2twitter)]
            if BLOG.post_is_local(idx):
                menu += [(LABELS.loc.pt_menu_offl_publ,self.offline_publish)]
        op = popup_menu(map(lambda x: x[0], menu) , LABELS.loc.pt_pmenu_posts)
        if op is not None:
            map(lambda x: x[1], menu)[op]()
    
    def comments(self):
        def cbk():
            self.refresh()
            return True
        if BLOG.posts:
            idx = app.body.current()
            if BLOG.post_is_remote(idx):           
                self.dlg = Comments(cbk)
                self.dlg.run()
                self.dlg.update(idx)  # update comments for current post
    
    def update(self):
        self.lock_ui(LABELS.loc.pt_info_downld_pt)
        BLOG.update_posts_cats_and_tags()
        self.unlock_ui()            

        if not BLOG.posts:
            note(LABELS.loc.pt_info_no_posts, "info")
        
        self.refresh()
    
    def delete(self):
        if BLOG.posts:
            idx = app.body.current()
            if BLOG.post_is_local(idx) and BLOG.post_is_remote(idx):
                # remote post with local changes - many delete option
                options = ((LABELS.loc.gm_no,lambda x: False),
                           (LABELS.loc.pt_list_yes_rem_pst,BLOG.delete_only_remote_post),
                           (LABELS.loc.pt_list_yes_loc_ch,BLOG.delete_only_local_post),
                           (LABELS.loc.pt_list_yes_del_all,BLOG.delete_post))
            else:
                # just local or remote - delete
                options = ((LABELS.loc.gm_no,lambda x: False),
                           (LABELS.loc.gm_yes,BLOG.delete_post))
            ny = popup_menu(map(lambda x:x[0],options),LABELS.loc.pt_pmenu_del_post)
            if ny is not None:
                if ny > 0:
                    self.lock_ui(LABELS.loc.pt_info_del_post)
                    funcs = map(lambda x:x[1],options)
                    res = funcs[ny](idx)
                    if res:
                        note(LABELS.loc.pt_info_post_del,"info")
                    else:
                        note(LABELS.loc.pt_err_cant_del_pt,"error")                            
                    self.unlock_ui() 
                    self.refresh()

    def new_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui()
            # send to WP
            np = BLOG.new_post(self.dlg.post_title,
                               self.dlg.contents,
                               self.dlg.categories,
                               self.dlg.tags,
                               self.dlg.publish)
            self.unlock_ui()
            
            if np == -1:
                return False
        elif self.dlg.save:
            # just save
            BLOG.save_new_post(self.dlg.post_title,
                               self.dlg.contents,
                               self.dlg.categories,
                               self.dlg.tags,
                               self.dlg.publish)
            
        self.refresh()
        return True
            
    def new(self):
        self.dlg = NewPost(self.new_cbk, u"", u"",
                           BLOG.category_names_list(), [],
                           BLOG.tag_names_list(), [],
                           True)
        self.dlg.run()

    def contents_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui()
            # send post to WP
            ok = BLOG.edit_post(self.dlg.post_title,
                                self.dlg.contents,
                                self.dlg.categories,
                                self.dlg.tags,
                                self.dlg.post_idx,
                                self.dlg.publish)
            self.unlock_ui()
            
            if not ok:
                return False
        elif self.dlg.save:
            # just save post
            BLOG.save_exist_post(self.dlg.post_title,
                                 self.dlg.contents,
                                 self.dlg.categories,
                                 self.dlg.tags,
                                 self.dlg.post_idx,
                                 self.dlg.publish)
        self.refresh()
        return True
        
    def contents(self):
        if BLOG.posts:
            idx = self.body.current()
            if self.download_contents(idx):
                publish = BLOG.posts[idx]['post_status'] == 'publish' # 'publish' or 'draft'
                self.dlg = EditPost(self.contents_cbk,
                                    BLOG.category_names_list(),
                                    BLOG.tag_names_list(),
                                    idx,
                                    publish)
                self.dlg.run()

    def download_contents(self,idx):
        # if post was not totally retrieved yet, fetch all data
        # only call this function if you have posts
        if BLOG.posts[idx].has_key('description') == False:
            self.lock_ui(LABELS.loc.pt_info_downld_post)
            ok = BLOG.get_post(idx)
            self.unlock_ui()
            if not ok:
                note(LABELS.loc.pt_err_cant_pst_cont, "error")
                return False
            
        return True
        
    def send2twitter(self):
        """ Send a post title to twitter. Just must be called if twitter is enabled
        """
        if BLOG.posts:
            idx = self.body.current()
            if BLOG.post_is_remote(idx):
                if self.download_contents(idx):
                    self.lock_ui(LABELS.loc.pt_info_send_twt+u".")
                    link = BLOG.posts[idx]['permaLink']
                    title = BLOG.posts[idx]['title']
                    api = s60twitter.TwitterApi(DB["twitter_user"],
                                                DB["twitter_pass"],
                                                BLOG.proxy)
                    self.set_title(LABELS.loc.pt_info_send_twt+u"..")
                    try:
                        tiny_link = api.tinyfy_url(link)
                    except:
                        note(LABELS.loc.pt_err_cant_tiny_url,"error")
                    else:
                        msg = title[:140-len(tiny_link)-1] + " " + tiny_link # twitter: 140 chars max
                        self.set_title(LABELS.loc.pt_info_send_twt+u"...")
                        try:
                            api.update(msg)
                        except:
                            note(LABELS.loc.pt_err_cant_send_twitter,"error")
                        else:
                            note(LABELS.loc.pt_info_twitter_updated,"info")

                    self.set_title(u"")                            
                    self.unlock_ui()
                    self.refresh()

    def offline_publish(self):
        if BLOG.posts:
            idx = self.body.current()
            if BLOG.post_is_local(idx):
                self.lock_ui()
                BLOG.offline_publish(idx)
                self.unlock_ui()
                self.refresh()
            
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 

        if not BLOG.posts:
            self.headlines = [ (LABELS.loc.pt_info_empty, LABELS.loc.pt_info_updt_pst_lst) ]
        else:
            self.headlines = []
            for p in BLOG.posts:
                status = u""
                (y, mo, d, h, m, s) = parse_iso8601(p['dateCreated'].value)
                if BLOG.post_is_only_local(p):
                    status = u"[@] "
                elif BLOG.post_is_local(p):
                    status = u"[*] "
                elif p.has_key('post_status'):
                    if p['post_status'] != 'publish':
                        status = u"[#]"

                line1 = status + u"%02d/%s/%02d  %02d:%02d " % (d,MONTHS[mo-1],y,h,m) 
                line2 = utf8_to_unicode(p['title'])
                self.headlines.append((line1 , line2))
                               
        self.last_idx = min(self.last_idx, len(self.headlines)-1) # avoiding problems after removing
        self.body.set_list(self.headlines, self.last_idx)

