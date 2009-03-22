# -*- coding: utf-8 -*-
import e32
from types import StringTypes
from appuifw import *
from window import Dialog
if float(e32.pys60_version[:3]) >= 1.9:
    import btsocket as socket
else:
    import socket
from wmutil import *
import key_codes
from persist import DB
from wpwrapper import BLOG
from wmlocale import LABELS

__all__ = [ "sel_access_point", "BlogSettings", "ProxySettings", "Settings" ]

def sel_access_point():
    """ Select the default access point. Return True if the selection was
        done or False if not
    """
    aps = socket.access_points()
    if not aps:
        note(LABELS.loc.st_err_no_access_point,"error")
        return False
    
    ap_labels = map( lambda x: x['name'], aps )
    item = popup_menu( ap_labels, LABELS.loc.st_query_access_points )
    if item is None:
        note(LABELS.loc.st_err_one_ap_req,"error")
        return False
    
    apo = socket.access_point( aps[item]['iapid'] )
    socket.set_default_access_point( apo )
    
    return True

class BlogSettings(Dialog):
    def __init__(self, cbk):
        self.user = DB["user"]
        self.passw = DB["pass"]
        self.blog = DB["blog"]
        self.num_posts = int(DB["num_posts"])
        self.num_comments = int(DB["num_comments"])
        self.email = DB["email"]
        self.realname = DB["realname"]
        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( LABELS.loc.st_menu_canc, self.cancel_app )]
        
        Dialog.__init__(self, cbk, LABELS.loc.st_info_blog_set, body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
            
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 
        values = [ (LABELS.loc.st_menu_blog_url, self.blog ),
                   (LABELS.loc.st_menu_blog_usr, self.user ),
                   (LABELS.loc.st_menu_blog_pwd, u"*"*len( self.passw )),
                   (LABELS.loc.st_menu_blog_npt, unicode( self.num_posts )),
                   (LABELS.loc.st_menu_blog_cpp, unicode( self.num_comments )),
                   (LABELS.loc.st_menu_blog_eml, self.email ),
                   (LABELS.loc.st_menu_blog_rnm, self.realname ) ]

        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        vars = ( "blog",
                 "user",
                 "passw",
                 "num_posts",
                 "num_comments",
                 "email",
                 "realname" )
        
        labels = ( LABELS.loc.st_menu_blog_url,
                   LABELS.loc.st_menu_blog_usr,
                   LABELS.loc.st_menu_blog_pwd,
                   LABELS.loc.st_menu_blog_npt,
                   LABELS.loc.st_menu_blog_cpp,
                   LABELS.loc.st_menu_blog_eml,
                   LABELS.loc.st_menu_blog_rnm )

        formats = ( "text",
                    "text",
                    "code",
                    "number",
                    "number",
                    "text",
                    "text" )
        
        val = query(labels[idx], formats[idx], self.__getattribute__(vars[idx]))
        if val is not None:
            if isinstance(val, StringTypes):
                val = val.strip()
            self.__setattr__( vars[idx],val )
            
        self.refresh()

class ProxySettings(Dialog):
    def __init__(self, cbk):
        self.proxy_enabled = DB["proxy_enabled"]
        self.proxy_address = DB["proxy_addr"]
        self.proxy_port = int(DB["proxy_port"])
        self.proxy_user = DB["proxy_user"]             
        self.proxy_password = DB["proxy_pass"]

        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( LABELS.loc.st_menu_canc, self.cancel_app )]
        
        Dialog.__init__(self, cbk, LABELS.loc.st_info_proxy_set, body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        
    def refresh(self):
        Dialog.refresh(self)
        if self.proxy_enabled == u"True":
            prx = LABELS.loc.st_menu_proxy_on
        else:
            prx = LABELS.loc.st_menu_proxy_off
        values = [ (LABELS.loc.st_menu_proxy_ena, prx ), \
                   (LABELS.loc.st_menu_proxy_add, self.proxy_address ), \
                   (LABELS.loc.st_menu_proxy_prt, unicode( self.proxy_port ) ), \
                   (LABELS.loc.st_menu_proxy_usr, self.proxy_user), \
                   (LABELS.loc.st_menu_proxy_pwd, u"*"*len( self.proxy_password ) ) ]
        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        if idx == 0:
            if self.proxy_enabled == u"True":
                self.proxy_enabled = u"False"
            else:
                self.proxy_enabled = u"True"
        elif self.proxy_enabled == u"True":
            if idx == 1:
                addr = query(LABELS.loc.st_query_proxy_add,"text", self.proxy_address)
                if addr is not None:
                    self.proxy_address = addr
            elif idx == 2:
                port = query(LABELS.loc.st_query_proxy_prt,"number", self.proxy_port)
                if port is not None:
                    self.proxy_port = port                         
            elif idx == 3:
                user = query(LABELS.loc.st_query_proxy_usr,"text", self.proxy_user)
                if user is not None:
                    self.proxy_user = user
                else:
                    self.proxy_user = u""
            elif idx == 4:
                password = query(LABELS.loc.st_query_proxy_pwd,"code", self.proxy_password)
                if password is not None:
                    self.proxy_password = password
                else:
                    self.proxy_password = u""
        self.refresh()

class TwitterSettings(Dialog):
    def __init__(self, cbk):
        self.twitter_enabled = DB["twitter_enabled"]
        self.twitter_user = DB["twitter_user"]             
        self.twitter_password = DB["twitter_pass"]

        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( LABELS.loc.st_menu_canc, self.cancel_app )]
        
        Dialog.__init__(self, cbk, LABELS.loc.st_info_twitter_set, body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        
    def refresh(self):
        Dialog.refresh(self)
        if self.twitter_enabled == u"True":
            twitter = LABELS.loc.st_menu_twitter_on
        else:
            twitter = LABELS.loc.st_menu_twitter_off
        values = [ (LABELS.loc.st_menu_twitter_ena, twitter ), \
                   (LABELS.loc.st_menu_proxy_usr, self.twitter_user), \
                   (LABELS.loc.st_menu_proxy_pwd, u"*"*len( self.twitter_password ) ) ]
        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        if idx == 0:
            if self.twitter_enabled == u"True":
                self.twitter_enabled = u"False"
            else:
                self.twitter_enabled = u"True"
        elif self.twitter_enabled == u"True":                        
            if idx == 1:
                user = query(LABELS.loc.st_query_twitter_usr,"text", self.twitter_user)
                if user is not None:
                    self.twitter_user = user
                else:
                    self.twitter_user = u""
            elif idx == 2:
                password = query(LABELS.loc.st_query_twitter_pwd,"code", self.twitter_password)
                if password is not None:
                    self.twitter_password = password
                else:
                    self.twitter_password = u""
        self.refresh()


class Settings(Dialog):
    def __init__(self,cbk):
        self.dlg = None
        self.body = Listbox( [(u"",u"")],self.update_value)
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_sets, self.body)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)        

    def refresh(self):
        Dialog.refresh(self)
        self.set_title(LABELS.loc.wm_menu_sets)
        idx = self.body.current()
        items = [ ( LABELS.loc.st_menu_blog,u""),
                  ( LABELS.loc.st_menu_proxy, u""),
                  ( LABELS.loc.st_menu_access_point, u""),
                  ( LABELS.loc.st_menu_lang, u""),
                  ( LABELS.loc.st_menu_twitter, u"")]
        self.body.set_list( items, idx )
        
    def update_value(self):
        idx = self.body.current()
        ( self.blog,
          self.proxy,
          self.access_point,
          self.language,
          self.twitter)[idx]()

    def blog_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            if self.dlg.blog[-1] == u"/":
                self.dlg.blog = self.dlg.blog[:-1]
            DB["blog"] = self.dlg.blog
            DB["user"] = self.dlg.user
            DB["pass"] = self.dlg.passw
            DB["email"] = self.dlg.email
            DB["realname"] = self.dlg.realname
            DB["num_posts"] = utf8_to_unicode( str(self.dlg.num_posts) )
            DB["num_comments"] = utf8_to_unicode( str(self.dlg.num_comments) )
            DB.save()
            BLOG.set_blog()
        self.unlock_ui()
        self.refresh()
        return True
    
    def blog(self):
        self.dlg = BlogSettings( self.blog_cbk )
        self.dlg.run()

    def proxy_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            DB["proxy_enabled"]= self.dlg.proxy_enabled
            DB["proxy_addr"] = self.dlg.proxy_address
            DB["proxy_user"] = self.dlg.proxy_user
            DB["proxy_pass"] = self.dlg.proxy_password
            DB["proxy_port"] = utf8_to_unicode( str(self.dlg.proxy_port) )
            DB.save()
            BLOG.set_blog()
        self.unlock_ui()
        self.refresh()
        return True
        
    def proxy(self):
        self.dlg = ProxySettings( self.proxy_cbk )
        self.dlg.run()

    def access_point(self):
        if sel_access_point():
            BLOG.set_blog()

    def twitter_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            DB["twitter_enabled"]= self.dlg.twitter_enabled
            DB["twitter_user"] = self.dlg.twitter_user
            DB["twitter_pass"] = self.dlg.twitter_password
            DB.save()
            BLOG.set_blog()
        self.unlock_ui()
        self.refresh()
        return True
    
    def twitter(self):
        self.dlg = TwitterSettings( self.twitter_cbk )
        self.dlg.run()
        
    def language(self):
        langs = [(LABELS.loc.st_menu_en_us, u"en_us"),
                 (LABELS.loc.st_menu_pt_br, u"pt_br"),
                 (LABELS.loc.st_menu_es, u"es"),
                 (LABELS.loc.st_menu_tr, u"tr"),
                 (LABELS.loc.st_menu_it, u"it"),
                 (LABELS.loc.st_menu_nl, u"nl"),
                 (LABELS.loc.st_menu_de, u"de"),
                 (LABELS.loc.st_menu_ro, u"ro"),
                 (LABELS.loc.st_menu_zh_cn, u"zh_cn")]
        langs.sort()
        item = popup_menu(map(lambda x:x[0], langs), LABELS.loc.st_pmenu_lang )
        if item is not None:
            loc = langs[item][1]
            if DB["language"] != loc:
                LABELS.set_locale(loc)
                DB["language"] = loc
                DB.save()
                self.refresh()
                BLOG.refresh() # update global defines

