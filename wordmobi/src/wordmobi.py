# -*- coding: utf-8 -*-
import sys
try:
    # http://discussion.forum.nokia.com/forum/showthread.php?p=575213
    # Try to import 'btsocket' as 'socket' - ignored on versions < 1.9.x
    sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass
import os
import time
import urllib
from beautifulsoup import BeautifulSoup
from urllibproxy import UrllibProxy
import simplejson as json
import e32
import key_codes
from appuifw import *
from window import Application, Dialog
from about import About
from settings import Settings, sel_access_point
from posts import Posts
from comments import Comments
from categories import Categories
from tags import Tags
from wpstats import Stats
import wordpresslib as wp
from wmutil import *
from wmproxy import UrllibTransport
from wmglobals import VERSION, DEFDIR, MIFFILE
from wpwrapper import BLOG
from persist import DB
from wmlocale import LABELS

__all__ = [ "WordMobi" ]
__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = VERSION
__copyright__ = "Copyright (c) 2008- Marcelo Barros de Almeida"
__license__ = "GPLv3"

class BlogManager(Dialog):
    def __init__(self,cbk,title):
        # TODO Better icons or remove them
        icons = [Icon(MIFFILE,8,8),
                 Icon(MIFFILE,6,6),
                 Icon(MIFFILE,4,4),
                 Icon(MIFFILE,2,2),
                 Icon(MIFFILE,16,16),
                 ]
        menu_labels = [ LABELS.loc.wm_menu_post,
                        LABELS.loc.wm_menu_comm,
                        LABELS.loc.wm_menu_cats,
                        LABELS.loc.wm_menu_tags,
                        LABELS.loc.wm_menu_stat,
                        ]
        funcs = [self.posts,
                 self.comments,
                 self.categories,
                 self.tags,
                 self.stats,
                 ]
        menu = map(lambda a,b: (a,b), menu_labels, funcs)
        menu += [(LABELS.loc.wm_menu_exit, self.close_app)]
        items = map(lambda a,b: (a,u"",b), menu_labels, icons)
        Dialog.__init__(self,cbk,title,Listbox(items,self.update_value),menu)
        Dialog.__init__(self,cbk,title,self.body,menu)

        self.dlg = None
        
        self.bind(key_codes.EKeyRightArrow, self.update_value)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)

    def key_left(self):
        self.close_app()
            
    def update_value(self):
        idx = self.body.current()
        ( self.posts,
          self.comments,
          self.categories,
          self.tags,
          self.stats
          )[idx]()

    def default_cbk(self):
        app.screen = 'normal'
        self.refresh()
        return True
        
    def posts(self):
        self.dlg = Posts(self.default_cbk)
        self.dlg.run()

    def comments(self):
        self.dlg = Comments(self.default_cbk)
        self.dlg.run()

    def categories(self):
        self.dlg = Categories(self.default_cbk)
        self.dlg.run()

    def tags(self):
        self.dlg = Tags(self.default_cbk)
        self.dlg.run()

    def stats(self):
        self.dlg = Stats(self.default_cbk)
        self.dlg.run()
    
class WordMobi(Application):
    
    def __init__(self):
        app.screen='normal' # TODO check all app.xyz use
        LABELS.set_locale(DB["language"])
        self.wp_icon = Icon(MIFFILE,14,14)
        self.blogs = json.loads(DB["blog_list"])
        items = [ (b["account"],b["blog"],self.wp_icon) for b in self.blogs ]
        menu = [(LABELS.loc.wm_menu_exit, self.close_app)] 
        Application.__init__(self,  u"Wordmobi", Listbox( items, self.check_update_value ))
        self._update_menu()

        # TODO
        # {
        # Temporary fix before changing how persistence is treated.
        # New persistence module must be created to avoid this line and e32db.
        __changed = False
        for n in range(len(self.blogs)):
            if not self.blogs[n].has_key("api_key"):
                self.blogs[n]["api_key"] = ""
                __changed = True
        if __changed:
            DB["blog_list"]=json.dumps(self.blogs)
            DB.save()
        #
        # }
        #
        self.dlg = None
        sel_access_point()

        self.bind(key_codes.EKeyRightArrow, self.check_update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)

    def _get_menu_labels(self):
        menu_labels = [ LABELS.loc.wm_menu_sets,
                        LABELS.loc.wm_menu_upgr,
                        LABELS.loc.wm_menu_abou ]
        return menu_labels

    def _get_menu_functions(self):
        funcs = [self.settings,
                 self.upgrade,
                 self.about]
        return funcs
        
    def check_update_value(self):
        if not self.ui_is_locked():
            idx = self.body.current()
            BLOG.set_blog(idx)
            self.dlg = BlogManager(self.default_cbk,self.blogs[idx]['account'])
            self.dlg.run()
            
    def default_cbk(self):
        self.refresh()
        return True

    def _update_menu(self):
        self.global_menu = map(lambda a,b: (a,b), self._get_menu_labels(), self._get_menu_functions())
        self.global_menu += [(LABELS.loc.wm_menu_exit, self.close_app)]
            
    def settings_cbk(self):
        if self.dlg.lang_changed:
            self._update_menu()
        self.blogs = json.loads(DB["blog_list"])
        items = [ (b["account"],b["blog"],self.wp_icon) for b in self.blogs ]
        self.body.set_list(items,0)
        self.refresh()
        return True
    
    def settings(self):
        self.dlg = Settings(self.settings_cbk)
        self.dlg.run()

    def ver2num(self,ver):
        ver = ver.split("-")[0] # does not use any -RC version
        a,b,c = map(lambda x,y: x*y, [10000,100,1],[int(v) for v in ver.split(".")])
        return a+b+c
        
    def upgrade(self):
        self.lock_ui(LABELS.loc.wm_info_check_updt)
        
        url = "http://code.google.com/p/wordmobi/wiki/LatestVersion"
        local_file = "web_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        local_file = os.path.join(DEFDIR, "cache", local_file)

        try:
            urlprx = UrllibProxy(BLOG.get_proxy())
            urlprx.urlretrieve(url, local_file)
        except:
            note(LABELS.loc.wm_err_upd_page % url,"error")
            ok = False
        else:
            ok = True

        if ok:
            html = open(local_file).read()
            soup = BeautifulSoup( html )
            addrs = soup.findAll('a')
            version = ""
            file_url = ""
            file_url_py19 = ""
            for addr in addrs:
                if addr.contents[0] == "latest_wordmobi_version":
                    version = addr["href"]
                elif addr.contents[0] == "wordmobi_sis_url":
                    file_url = addr["href"]
                elif addr.contents[0] == "wordmobi_sis_url_py19":
                    file_url_py19 = addr["href"]

            if version and file_url and file_url_py19:
                version = version[version.rfind("/")+1:]
                num_rem_ver = self.ver2num(version)
                num_loc_ver = self.ver2num(VERSION)
                if (num_loc_ver >= num_rem_ver) and (VERSION.find('RC') == -1):
                    # RC versions gives to the user the upgrading decision
                    note(LABELS.loc.wm_info_ver_is_updt, "info")
                else:
                    yn = popup_menu( [LABELS.loc.gm_yes,LABELS.loc.gm_no],
                                     LABELS.loc.wm_pmenu_download % (version) )
                    if yn is not None:
                        if yn == 0:
                            if float(e32.pys60_version[:3]) >= 1.9:
                                furl = file_url_py19
                            else:
                                furl = file_url
                            sis_name = furl[furl.rfind("/")+1:]
                            local_file = os.path.join(DEFDIR, "updates", sis_name)

                            self.set_title( LABELS.loc.wm_info_downloading )
                            try:
                                urlprx = UrllibProxy(BLOG.get_proxy())
                                urlprx.urlretrieve(furl, local_file)
                            except:
                                note(LABELS.loc.wm_err_downld_fail % sis_name, "error")
                            else:
                                msg = LABELS.loc.wm_info_downld_ok % (sis_name,DEFDIR)
                                note( msg , "info")

            else:
                note(LABELS.loc.wm_err_upd_info,"error")
                
        self.set_title( u"Wordmobi" )
        self.unlock_ui()
        self.refresh()

    def close_app(self):
        ny = popup_menu( [LABELS.loc.gm_yes, LABELS.loc.gm_no], LABELS.loc.wm_pmenu_exit )
        if ny is not None:
            if ny == 0:
                BLOG.save()
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
            note(LABELS.loc.wm_err_cache_cleanup % cache,"error")
            
    def about(self):
        self.dlg = About(self.default_cbk)
        self.dlg.run()
                
if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
