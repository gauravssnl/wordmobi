# -*- coding: utf-8 -*-
import e32
from appuifw import *
import types

class BlogSettings(object):
    def __init__(self,
                 cbk,
                 blog_url= u"http://blogname.wordpress.com",                 
                 username = u"",
                 password = u"",             
                 num_posts = 10,
                 num_comments = 20):

        self.cbk = cbk
        self.username = username
        self.password = password
        self.blog_url = blog_url
        self.num_posts = num_posts
        self.num_comments = num_comments
        
        self.body = Listbox( [ (u"",u"") ], self.update_value )
        self.cancel = False
        self.last_idx = 0

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = u"Settings"

        values = [ (u"Blog URL:", self.blog_url ), \
                   (u"Username:", self.username ), \
                   (u"Password:", u"*"*len( self.password )), \
                   (u"Number of Posts:", unicode( self.num_posts )),
                   (u"Number of Comments:", unicode( self.num_comments ))]

        app.body = self.body
        app.body.set_list( values, self.last_idx )
        app.menu = [( u"Cancel", self.cancel_app )]        
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.cbk( ( self.blog_url, self.username, self.password, self.num_posts, self.num_comments) )
        else:
            self.cbk( (None,) )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        vars = ( "blog_url", "username", "password", "num_posts", "num_comments" )
        labels = ( u"Blog URL:", u"Username:", u"Password:", u"Number of posts:", u"Number of comments" )
        formats = ( "text", "text", "code", "number", "number" )
        
        val = query(labels[idx], formats[idx], self.__getattribute__(vars[idx]))
        if val is not None:
            if type(val) in ( types.UnicodeType , types.StringType ):
                val = val.strip()
            self.__setattr__( vars[idx],val )
  
        self.refresh()
        
    def run(self):
        self.refresh()

class ProxySettings(object):
    def __init__(self,
                 cbk,
                 proxy_enabled,
                 proxy_address,
                 proxy_port,
                 proxy_user,                 
                 proxy_password):
        
        self.cbk = cbk
        self.proxy_enabled = proxy_enabled
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user             
        self.proxy_password = proxy_password
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.cancel = False
        self.last_idx = 0
        self.menu = [ ( u"Cancel", self.cancel_app ) ]
        self.app_title = u"Proxy settings"

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = self.app_title

        self.lst_values = [ (u"Enabled", self.proxy_enabled  ), \
                            (u"Address", self.proxy_address ), \
                            (u"Port", unicode( self.proxy_port ) ), \
                            (u"Username", self.proxy_user), \
                            (u"Password", u"*"*len( self.proxy_password ) ) ]

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
            #set_default_access_point(None)
            self.lock_ui()
            if self.cbk( (self.proxy_enabled, self.proxy_address, self.proxy_port, \
                          self.proxy_user, self.proxy_password) ) == False:
                self.unlock_ui()
                self.refresh()
        else:
            self.cbk( None )

    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update_value( app.body.current() )

    def update_value(self,idx):
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
            elif idx == 4:
                password = query(u"Proxy username:","code", self.proxy_password)
                if password is not None:
                    self.proxy_password = password     
        self.refresh()
        
    def run(self):
        self.refresh()


if __name__ == "__main__":

    lock = e32.Ao_lock()
    
    def cbk( x ):
        print x
        lock.signal()
        
    dlg = Settings( cbk )
    dlg.run()
    
    lock.wait()
