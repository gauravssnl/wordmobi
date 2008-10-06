# -*- coding: utf-8 -*-
#import sys
#sys.path.append("e:\\python")

import e32

EMUL = e32.in_emulator()

if EMUL:
    import  datetime
else:
    import sys
    sys.path.append("e:\\python")
    import dt as datetime
    
import appuifw as gui
import os.path
import wordpresslib as wp
import e32dbm

class WordMobi:

    if EMUL:
        DEFDIR = "__wordmoby__/"
        DEFCFG = "wordmobi"
    else:
        DEFDIR = u"c:\\wordmobi\\"
        DEFCFG = u"wordmobi"

    DBNAME = DEFDIR+DEFCFG

    def unicode(self,s):
        if not EMUL:
            return s
        else:
            return unicode(s,'utf-8',errors='ignore')

    def __init__(self):
        self.cfg = {"user":u"username", "pass":u"password", "blog":u"blogname" }
        #self.posts = {}
        self.body = None

    def save_cfg(self):
        if not os.path.exists(WordMobi.DEFDIR):
            os.mkdir(WordMobi.DEFDIR)

        db = e32dbm.open(WordMobi.DBNAME,"c")    
        for k,v in self.cfg.iteritems():
            db[k] = v

        db.close()

    def load_cfg(self):
        try:
            db = e32dbm.open(WordMobi.DBNAME,"c")
            for k in self.cfg.keys():
                self.cfg[k] = unicode(db[k])
            db.close()
        except:
            self.save_cfg()

    def close_app(self):
        self.app_lock.signal()

    def recent_posts(self):
        url = "http://%s.wordpress.com/xmlrpc.php" % self.cfg["blog"]
        blog = wp.WordPressClient(url, self.cfg["user"], self.cfg["pass"])
        blog.selectBlog(0)
        recentPosts = 10
        
        contents = []

        try:
            self.posts = blog.getRecentPosts(recentPosts)
        except:
            gui.note(u"Could not connect to blog %s. Please, check your blog settings." % self.cfg["blog"],"info")
            return

        for p in self. posts:
            contents.append( self.unicode( p['title'] ) )

        self.body.set_list( contents )

    def new_post(self):
        gui.app.title = u"wordmobi new post"
        fields = [ (u"Title","text",""), (u"Body","text","") ]
        f = gui.Form( fields,gui.FFormEditModeOnly )
        f.execute()
        tit = f[0][2]
        bod = f[1][2]

        if not tit or not bod:
            gui.note(u"Invalid post","info")
            return

        url = "http://%s.wordpress.com/xmlrpc.php" % self.cfg["blog"]
        blog = wp.WordPressClient(url, self.cfg["user"], self.cfg["pass"])
        blog.selectBlog(0)

        post = wp.WordPressPost()
        post.title = tit
        post.description = bod
        try:
            new_post = blog.newPost(post, True)
        except:
            gui.note(u"Error when connecting to blog %s" % self.cfg["blog"],"info")        

        gui.app.title = u"wordmobi Posts"

    def list_comments(self):
        gui.app.title = u"wordmobi comments"
        gui.note( u"Comments cbk", "info" )
        gui.app.title = u"wordmobi Posts"

    def about_wordmobi(self):
        gui.app.title = u"Wordmobi about"
        gui.note( u"Wordmobi\nby\nJedizone", "info" )
        gui.app.title = u"wordmobi Posts"

    def listbox_cbk(self):
        idx = self.body.current()
        gui.note( u"List cbk %d" % idx, "info" )

    def config_wordmobi(self):
        gui.app.title = u"wordmobi config"

        fields = [ (u"Blog Name","text",self.cfg["user"]), \
                   (u"Username","text",self.cfg["user"]), \
                   (u"Password","text",self.cfg["pass"]) ] # use code instead in s60
        
        f = gui.Form(fields,gui.FFormEditModeOnly)
        f.execute()
        blog = f[0][2]
        user = f[1][2]
        pwd  = f[2][2]
        
        if not user or not pwd or not blog:
            gui.note(u"Invalid config","info")
            return

        conf = { "user":user, "pass":pwd, "blog":blog }
        self.cfg = conf
        self.save_cfg()
        gui.app.title = u"wordmobi Posts"

    def main(self):
        gui.app.exit_key_handler = self.close_app
        gui.app.title = u"wordmobi Posts"
        gui.app.menu = [( u"Posts", self.recent_posts ), 
                        ( u"Comments", self.list_comments ), 
                        ( u"New Post", self.new_post ),
                        ( u"Settings", self.config_wordmobi ),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]

	self.posts = {}
        self.body = gui.Listbox([ u"Press Posts for updating" ], self.listbox_cbk )
        gui.app.body = self.body
        self.load_cfg()
        self.app_lock = e32.Ao_lock()
        self.app_lock.wait()

if __name__ == "__main__":

    wm = WordMobi()
    wm.main()
