from window import Dialog
from appuifw import *
import key_codes

from wmglobals import VERSION
from persist import DB
from wmlocale import LABELS

__all__ = [ "About" ]

class About(Dialog):
    def __init__(self,cbk):
        self.items = [ ( u"Wordmobi %s" % VERSION, LABELS.loc.ab_menu_wordmobi_defi_val ),
                       ( LABELS.loc.ab_menu_wordmobi_auth, u"Marcelo Barros de Almeida" ),
                       ( LABELS.loc.ab_menu_wordmobi_mail, u"marcelobarrosalmeida@gmail.com" ),
                       ( LABELS.loc.ab_menu_wordmobi_srcc, u"http://wordmobi.googlecode.com" ),
                       ( LABELS.loc.ab_menu_wordmobi_blog, u"http://wordmobi.wordpress.com" ),
                       ( LABELS.loc.ab_menu_wordmobi_lics, u"GNU GPLv3" ),
                       ( LABELS.loc.ab_menu_wordmobi_warn, LABELS.loc.ab_menu_wordmobi_warn_val ) ]
        values = map( lambda x: (x[0], x[1]), self.items )
        menu = [(LABELS.loc.wm_menu_exit, self.close_app)]
        
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_abou, Listbox( values, self.show_info ), menu)
        
        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.show_info)

    def show_info(self):
        idx = self.body.current()
        note( self.items[idx][1],"info" )
        

