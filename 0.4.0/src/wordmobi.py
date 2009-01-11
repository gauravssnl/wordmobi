# -*- coding: utf-8 -*-
import os
import time
import urllib
from beautifulsoup import BeautifulSoup
from xmlrpclib import DateTime

import e32
import e32dbm
import key_codes
from appuifw import *
from window import Application
from about import About
from settings import Settings, sel_access_point
from posts import Posts
from comments import Comments
from categories import Categories
import wordpresslib as wp
from wmutil import *
from wmproxy import UrllibTransport
from wmglobals import VERSION, DEFDIR, MIFFILE
from wpwrapper import BLOG
from persist import DB

__all__ = [ "WordMobi" ]
__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = VERSION
__copyright__ = "Copyright (c) 2008- Marcelo Barros de Almeida"
__license__ = "GPLv3"

class WordMobi(Application):
    
    def __init__(self):
        mif = unicode(os.path.join(DEFDIR,MIFFILE))
        items = [ ( u"Posts", u"", Icon(mif,16392,16392) ),
                  ( u"Comments", u"", Icon(mif,16390,16390) ),
                  ( u"Categories", u"", Icon(mif,16388,16388) ),
                  ( u"Tags", u"", Icon(mif,16386,16386) ),
                  ( u"Settings", u"", Icon(mif,16394,16394) ),
                  ( u"Upgrade", u"", Icon(mif,16396,16396) ),
                  ( u"About", u"", Icon(mif,16384,16384) )]
        #items = [ ( u"Posts", u""),
        #          ( u"Comments", u"" ),
        #          ( u"Categories", u"" ),
        #          ( u"Tags", u"" ),
        #          ( u"Settings", u""),
        #          ( u"Upgrade", u"" ),
        #          ( u"About", u"" )]         
        
        Application.__init__(self,  u"Wordmobi", Listbox( items, self.check_update_value ))

        self.dlg = None

        sel_access_point()
        BLOG.set_blog()

        self.bind(key_codes.EKeyRightArrow, self.check_update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)

    def check_update_value(self):
        if not self.ui_is_locked():
            self.update_value()
            
    def update_value(self):
        idx = self.body.current()
        ( self.posts, self.comments, self.categories, self.tags, self.settings, self.upgrade, self.about)[idx]()

    def default_cbk(self):
        #self.unlock_ui()
        self.refresh()
        return True

    def tags(self):
        note(u"Not supported yet","info")
        
    def posts(self):
        self.dlg = Posts(self.default_cbk)
        self.dlg.run()

    def comments(self):
        self.dlg = Comments(self.default_cbk)
        self.dlg.run()

    def categories(self):
        self.dlg = Categories(self.default_cbk)
        self.dlg.run()
        
    def settings(self):
        self.dlg = Settings(self.default_cbk)
        self.dlg.run()

    def ver2num(self,ver):
        a,b,c = map(lambda x,y: x*y, [10000,100,1],[int(v) for v in ver.split(".")])
        return a+b+c
        
    def upgrade(self):
        if DB["proxy_enabled"] == u"True" and len(DB["proxy_user"]) > 0:
            note(u"Proxy authentication not supported for this feature","info")
            return

        self.lock_ui(u"Checking update page...")
        
        url = "http://code.google.com/p/wordmobi/wiki/LatestVersion"
        local_file = "web_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        local_file = os.path.join(DEFDIR, "cache", local_file)

        #title = self.get_title() 
        #self.set_title( u"Checking update page..." )
        ok = True
        try:
            urllib.urlretrieve( url, local_file )
        except:
            note(u"Impossible to access update page %s" % url,"error")
            ok = False

        if ok:
            html = open(local_file).read()
            soup = BeautifulSoup( html )
            addrs = soup.findAll('a')
            version = ""
            file_url = ""
            for addr in addrs:
                if addr.contents[0] == "latest_wordmobi_version":
                    version = addr["href"]
                elif addr.contents[0] == "wordmobi_sis_url":
                    file_url = addr["href"]

            if version and file_url:
                version = version[version.rfind("/")+1:]
                num_rem_ver = self.ver2num(version)
                num_loc_ver = self.ver2num(VERSION)
                if num_loc_ver >= num_rem_ver:
                    note(u"Your version is already updated", "info")
                else:
                    yn = popup_menu( [ u"Yes", u"No"], "Download %s ?" % (version) )
                    if yn is not None:
                        if yn == 0:
                            sis_name = file_url[file_url.rfind("/")+1:]
                            local_file = os.path.join(DEFDIR, "updates", sis_name)

                            self.set_title( u"Downloading ..." )
                            ok = True
                            try:
                                urllib.urlretrieve( file_url, local_file )
                            except:
                                note(u"Impossible to download %s" % sis_name, "error")
                                ok = False

                            if ok:
                                note(u"%s downloaded in " + unicode(DEFDIR) + \
                                     "updates. Please, install it." % sis_name, "info")

            else:
                note(u"Upgrade information missing.","error")
                
        self.set_title( u"Wordmobi" )
        self.unlock_ui()
        self.refresh()

    def close_app(self):
        ny = popup_menu( [u"Yes", u"No"], u"Exit ?" )
        if ny is not None:
            if ny == 0:
                self.clear_cache()
                Application.close_app(self)

    def clear_cache(self):
        not_all = False
        cache = os.path.join(DEFDIR, "cache")
        entries = os.listdir( cache )
        for e in entries:
            fname = os.path.join(cache,e)
            if os.path.isfile( fname ):
                try:
                    os.remove( fname )
                except:
                    not_all = True
        if not_all:
            note(u"Not all files in %s could be removed. Try to remove them later." % cache,"error")
            
    def about(self):
        self.dlg = About(self.default_cbk)
        self.dlg.run()
        
if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
