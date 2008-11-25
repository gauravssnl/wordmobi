# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")

import e32

EMUL = e32.in_emulator()

if not EMUL:
    sys.path.append("e:\\python")
    
import os
import e32dbm

class Persist(dict):

    if EMUL:
        DEFDIR = "__wordmoby__/"
        DEFCFG = "wordmobi"
    else:
        DEFDIR = "c:\\wordmobi\\"
        DEFCFG = "wordmobi"

    DBNAME = DEFDIR+DEFCFG

    DEFVALS = {"user":u"username",
               "pass":u"password",
               "blog":u"blogname",
               "num_posts":u"20",
               "categories":u""}
    
    def __init__(self):
        
        super(Persist,self).__init__()
        
        if not os.path.exists(Persist.DEFDIR):
            os.makedirs(Persist.DEFDIR)
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
        db = e32dbm.open(Persist.DBNAME,"c")
        for k in Persist.DEFVALS.iterkeys():
            self.__setitem__(k,unicode(db[k]))
        db.close()

    # TODO reise exceptions for keys that not belong to DEVALS


    
