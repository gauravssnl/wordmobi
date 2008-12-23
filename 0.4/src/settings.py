# -*- coding: utf-8 -*-
import e32
from types import StringTypes
from appuifw import *
from window import Dialog
from socket import select_access_point, access_point, access_points, set_default_access_point
import wordmobi
from wmutil import *
import key_codes

__all__ = [ "sel_access_point", "BlogSettings", "ProxySettings", "Settings" ]

def sel_access_point():
    """ Select the default access point. Return True if the selection was
        done or False if not
    """
    aps = access_points()
    if not aps:
        note(u"Could't find any access point.","error")
        return False
    
    ap_labels = map( lambda x: x['name'], aps )
    item = popup_menu( ap_labels, u"Access points:" )
    if item is None:
        note(u"At least one access point is required.","error")
        return False
    
    apo = access_point( aps[item]['iapid'] )
    set_default_access_point( apo )
    
    return True

class BlogSettings(Dialog):
    def __init__(self, cbk):
        self.user = wordmobi.DB["user"]
        self.passw = wordmobi.DB["pass"]
        self.blog = wordmobi.DB["blog"]
        self.num_posts = int(wordmobi.DB["num_posts"])
        self.num_comments = int(wordmobi.DB["num_comments"])
        self.email = wordmobi.DB["email"]
        self.realname = wordmobi.DB["realname"]
        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( u"Cancel", self.cancel_app )]
        
        Dialog.__init__(self, cbk, u"Blog settings", body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
            
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 
        values = [ (u"Blog URL:", self.blog ), \
                   (u"Username:", self.user ), \
                   (u"Password:", u"*"*len( self.passw )), \
                   (u"Email (for comments):",  self.email ), \
                   (u"Real name (for comments):",  self.realname ), \
                   (u"Number of posts:", unicode( self.num_posts )),
                   (u"Number of comments per post:", unicode( self.num_comments )) ]

        app.body.set_list( values, self.last_idx )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        vars = ( "blog", "user", "passw", "email", "realname", "num_posts", "num_comments" )
        labels = ( u"Blog URL:", u"Username:", u"Password:", u"Email (for comments):", \
                   u"Real name (for comments):", u"Number of posts:", u"Number of comments per post" )
        formats = ( "text", "text", "code", "text", "text", "number", "number" )
        
        val = query(labels[idx], formats[idx], self.__getattribute__(vars[idx]))
        if val is not None:
            if isinstance(val, StringTypes):
                val = val.strip()
            self.__setattr__( vars[idx],val )
            
        self.refresh()

class ProxySettings(Dialog):
    def __init__(self, cbk):
        self.proxy_enabled = wordmobi.DB["proxy_enabled"]
        self.proxy_address = wordmobi.DB["proxy_addr"]
        self.proxy_port = int(wordmobi.DB["proxy_port"])
        self.proxy_user = wordmobi.DB["proxy_user"]             
        self.proxy_password = wordmobi.DB["proxy_pass"]

        self.last_idx = 0
        body =  Listbox( [ (u"",u"") ], self.update_value )
        menu = [( u"Cancel", self.close_app )]
        
        Dialog.__init__(self, cbk, u"Proxy settings", body,  menu)

        self.bind(key_codes.EKeyLeftArrow, self.cancel_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        
    def refresh(self):
        Dialog.refresh(self)
        values = [ (u"Enabled", self.proxy_enabled  ), \
                   (u"Address", self.proxy_address ), \
                   (u"Port", unicode( self.proxy_port ) ), \
                   (u"Username", self.proxy_user), \
                   (u"Password", u"*"*len( self.proxy_password ) ) ]

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
                addr = query(u"Proxy address:","text", self.proxy_address)
                if addr is not None:
                    self.proxy_address = addr
            elif idx == 2:
                port = query(u"Proxy port:","number", self.proxy_port)
                if port is not None:
                    self.proxy_port = port                         
            elif idx == 3:
                user = query(u"Proxy username:","text", self.proxy_user)
                if user is not None:
                    self.proxy_user = user
                else:
                    self.proxy_user = u""
            elif idx == 4:
                password = query(u"Proxy username:","code", self.proxy_password)
                if password is not None:
                    self.proxy_password = password
                else:
                    self.proxy_password = u""
        self.refresh()

class Settings(Dialog):
    def __init__(self,cbk):
        self.dlg = None
        items = [ ( u"Blog",u""),
                  ( u"Proxy", u""),
                  ( u"Access Point", u"") ]

        Dialog.__init__(self, cbk, u"Settings", Listbox( items, self.update_value ) )

        self.bind(key_codes.EKeyRightArrow, self.update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)        

    def update_value(self):
        idx = self.body.current()
        ( self.blog, self.proxy, self.access_point)[idx]()

    def blog_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            wordmobi.DB["blog"]= self.dlg.blog
            wordmobi.DB["user"] = self.dlg.user
            wordmobi.DB["pass"] = self.dlg.passw
            wordmobi.DB["email"] = self.dlg.email
            wordmobi.DB["realname"] = self.dlg.realname
            wordmobi.DB["num_posts"] = utf8_to_unicode( str(self.dlg.num_posts) )
            wordmobi.DB["num_comments"] = utf8_to_unicode( str(self.dlg.num_comments) )
            wordmobi.DB.save()
            wordmobi.BLOG.set_blog()
        self.unlock_ui()
        self.refresh()
        return True
    
    def blog(self):
        self.dlg = BlogSettings( self.blog_cbk )
        self.dlg.run()

    def proxy_cbk(self):
        self.lock_ui()
        if not self.dlg.cancel:
            wordmobi.DB["proxy_enabled"]= self.dlg.proxy_enabled
            wordmobi.DB["proxy_addr"] = self.dlg.proxy_address
            wordmobi.DB["proxy_user"] = self.dlg.proxy_user
            wordmobi.DB["proxy_pass"] = self.dlg.proxy_password
            wordmobi.DB["proxy_port"] = utf8_to_unicode( str(self.dlg.proxy_port) )
            wordmobi.DB.save()
            wordmobi.BLOG.set_blog()
        self.unlock_ui()
        self.refresh()
        return True
        
    def proxy(self):
        self.dlg = ProxySettings( self.proxy_cbk )
        self.dlg.run()

    def access_point(self):
        if sel_access_point():
            wordmobi.BLOG.set_blog()
    
