from window import Dialog
from wordmobi import * #__version__
from appuifw import Listbox
import wordmobi
import key_codes

class About(Dialog):
    def __init__(self,cbk):
        self.items = [ ( u"Wordmobi %s" % wordmobi.VERSION, u"A Wordpress client" ),
                       ( u"Author", u"Marcelo Barros de Almeida" ),
                       ( u"Email", u"marcelobarrosalmeida@gmail.com" ),
                       ( u"Source code", u"http://wordmobi.googlecode.com" ),
                       ( u"Blog", u"http://wordmobi.wordpress.com" ),
                       ( u"License", u"GNU GPLv3" ),
                       ( u"Warning", u"Use at your own risk" ) ]

        values = map( lambda x: (x[0], x[1]), self.items )
        Dialog.__init__(self, cbk, u"About", Listbox( values, self.show_info ) )
        self.bind(key_codes.EKeyLeftArrow, self.close)

    def show_info(self):
        idx = app.body.current()
        note( self.items[idx][1],"info" )
        

