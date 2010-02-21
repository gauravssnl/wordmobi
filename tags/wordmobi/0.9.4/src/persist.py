# -*- coding: utf-8 -*-
import os
import e32dbm
from wmglobals import DEFDIR, MIFFILE
from wmutil import *

__all__ = [ "Persist", "DB" ]

class Persist(dict):
    DBNAME = unicode(os.path.join(DEFDIR,"wordmobi"))
    DEFVALS = {"blog_list":u'[{"account":"Account name","user":"user name","pass":"password","blog":"http://blogname.wordpress.com","num_posts":10,"num_comments":20,"api_key":""}]',
               "proxy_user":u"",
               "proxy_pass":u"",
               "proxy_addr":u"",
               "proxy_port":u"8080",
               "proxy_enabled":u"False",
               "twitter_enabled":u"False",               
               "twitter_user":u"",
               "twitter_pass":u"",               
               "language":u""}
    
    def __init__(self):
        dict.__init__(self)
        self.check_dirs()
        self.load()
            
    def save(self):
        db = e32dbm.open(Persist.DBNAME,"c")
        for k in self.DEFVALS.iterkeys():
            db[k] = self.__getitem__(k)
        db.close()

    def load(self):
        try:
            db = e32dbm.open(self.DBNAME,"w")
        except:
            db = e32dbm.open(self.DBNAME,"n")
            
        for k in self.DEFVALS.iterkeys():
            try:
                self.__setitem__(k,utf8_to_unicode( db[k] ))
            except:
                self.__setitem__(k,self.DEFVALS[k])
        db.close()

    def check_dirs(self):
        dirs = (DEFDIR,
                os.path.join(DEFDIR,"cache"),
                os.path.join(DEFDIR,"images"),
                os.path.join(DEFDIR,"updates"))
        for d in dirs:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except:
                    note(u"Could't create directory %s" % d,"error")
        
DB = Persist()

