# -*- coding: utf-8 -*-
import e32
import os
import e32dbm
from appuifw import *

class Persist(dict):
    DEFDIR = "e:\\wordmobi\\"
    DBNAME = os.path.join(DEFDIR,"wordmobi")
    DEFVALS = {"user":u"username",
               "pass":u"password",
               "blog":u"http://blogname.wordpress.com",
               "num_posts":u"10",
               "num_comments":u"20",
               "categories":u"",
               "proxy_user":u"",
               "proxy_pass":u"",
               "proxy_addr":u"",
               "proxy_port":u"8080",
               "proxy_enabled":u"False"}
    
    def __init__(self):
        # make me singleton !
        super(Persist,self).__init__()
        if not os.path.exists(Persist.DEFDIR):
            os.makedirs(Persist.DEFDIR)
            os.makedirs(os.path.join(Persist.DEFDIR,"cache"))
            os.makedirs(os.path.join(Persist.DEFDIR,"images"))
            for k,v in Persist.DEFVALS.iteritems():
                self.__setitem__(k,v)
            self.save()
        else:
            self.load()
            
    def save(self):
        db = e32dbm.open(Persist.DBNAME,"c")
        for k in Persist.DEFVALS.iterkeys():
            db[k] = self.__getitem__(k)
        db.close()

    def load(self):
        db = e32dbm.open(Persist.DBNAME,"w")
        for k in Persist.DEFVALS.iterkeys():
            try:
                self.__setitem__(k,unicode(db[k]))
            except:
                self.__setitem__(k,Persist.DEFVALS[k])
        db.close()

    # TODO reise exceptions for keys that not belong to DEVALS


    
