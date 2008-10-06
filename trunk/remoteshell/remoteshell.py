import e32
import appuifw as gui
import e32dbm
import btconsole
from socket import *
import os.path

class RemoteShell:

    DEFDIR = u"c:\\remoteshell\\"
    DEFCFG = u"remoteshell"
    DBNAME = DEFDIR+DEFCFG

    def __init__(self):
        self.cfg = { "ip":u"0.0.0.0" }
        self.body = None

    def save_cfg(self):
        if not os.path.exists(RemoteShell.DEFDIR):
            os.mkdir(RemoteShell.DEFDIR)

        db = e32dbm.open(RemoteShell.DBNAME,"c")    
        for k,v in self.cfg.iteritems():
            db[k] = v

        db.close()

    def load_cfg(self):
        try:
            db = e32dbm.open(RemoteShell.DBNAME,"c")
            for k in self.cfg.keys():
                self.cfg[k] = unicode(db[k])
            db.close()
        except:
            self.save_cfg()

    def close_app(self):
        #self.app_lock.signal()
	gui.app.set_exit()

    def about(self):
        gui.note( u"RemoteShell\nMarcelo Barros de Almeida\nmarcelobarrosalmeida@gmail.com", "info" )

    def config(self):
        fields = [ (u"Svr IP","text",self.cfg["ip"]) ]
        f = gui.Form(fields,gui.FFormEditModeOnly)
        f.execute()
        ip = f[0][2]
        ip = ip.strip()

        if not ip:
            gui.note(u"Invalid config","info")
            return False

        self.cfg = { "ip":ip, }
        self.save_cfg()
        return True

    def main(self):
        gui.app.exit_key_handler = self.close_app
        gui.app.title = u"Remote Shell"
        gui.app.menu = [ ( u"About", self.about ), ( u"Exit", self.close_app )]
        self.load_cfg()
        self.config()

        sock = socket(AF_INET,SOCK_STREAM)
        sock.connect((self.cfg["ip"],1025))
        btconsole.run_with_redirected_io(sock,btconsole.interact, None, None, locals())

        #self.app_lock = e32.Ao_lock()
        #self.app_lock.wait()
        

if __name__ == "__main__":

    rm = RemoteShell()
    rm.main()
