# -*- coding: utf-8 -*-
import e32
from appuifw import *
import types
            
class Settings(object):
    def __init__(self,
                 cbk,
                 blog_url= u"http://blogname.wordpress.com",                 
                 username = u"",
                 password = u"",             
                 num_posts = 5):

        self.cbk = cbk
        self.username = username
        self.password = password
        self.blog_url = blog_url
        self.num_posts = num_posts
        
        self.body = Listbox( [ (u"",u"") ], self.update_value )
        self.cancel = False
        self.last_idx = 0

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = u"Settings"

        values = [ (u"Blog URL:", self.blog_url ), \
                   (u"Username:", self.username ), \
                   (u"Password:", u"*"*len( self.password )), \
                   (u"Number of Posts:", unicode( self.num_posts ) ) ]

        app.body = self.body
        app.body.set_list( values, self.last_idx )
        app.menu = [( u"Save", self.close_app ),\
                        ( u"Cancel", self.cancel_app )]        
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.cbk( ( self.blog_url, self.username, self.password, self.num_posts) )
        else:
            self.cbk( (None,None,None,None) )

    def update_value(self):
        idx = app.body.current()
        self.last_idx = idx
        
        vars = ( "blog_url", "username", "password", "num_posts" )
        labels = ( u"Blog URL:", u"Username:", u"Password:", u"Number of posts:" )
        formats = ( "text", "text", "code", "number" )
        
        val = query(labels[idx], formats[idx], self.__getattribute__(vars[idx]))
        if val is not None:
            if type(val) in ( types.UnicodeType , types.StringType ):
                val = val.strip()
            self.__setattr__( vars[idx],val )
  
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
