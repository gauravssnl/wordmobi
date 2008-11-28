# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32
import dt as datetime
import appuifw as gui
import os.path
import wordpresslib as wp
import e32dbm
from persist import Persist
from newpost import NewPost
from editpost import EditPost
import re

VERSION = "0.1.3"

def decode_html(line):
    "http://mail.python.org/pipermail/python-list/2006-April/378536.html"
    pat = re.compile(r'&#(\d+);')
    def sub(mo):
        return unichr(int(mo.group(1)))
    return pat.sub(sub, unicode(line))

def parse_iso8601(val):
    "Returns a tupple with (yyyy, mm, dd, hh, mm, ss). Argument is provided by xmlrpc DateTime.value"
    dt,tm= val.split('T')
    tm = tm.split(':')
    return (int(dt[:4]),int(dt[4:6]),int(dt[6:8]),int(tm[0]),int(tm[1]),int(tm[2]))
    
class WordMobi:
    def unicode(self,s):
        return unicode(s,'utf-8',errors='ignore')

    def __init__(self):
        self.lock = e32.Ao_lock()
        self.posts = None
        self.cats = [u"Uncategorized"]
        self.headlines = [ u"<empty>" ]        
        self.db = Persist()
        self.db.load()
        self.body = gui.Listbox( self.headlines, self.post_popup )
        self.blog = None
        
        self.refresh()

    def connect(self):
        if self.blog is None:
            try:
                url = "http://%s.wordpress.com/xmlrpc.php" % self.db["blog"]
                self.blog = wp.WordPressClient(url, self.db["user"], self.db["pass"])
            except:
                gui.note(u"Error when connecting to blog %s" % self.db["blog"],"info")
                return False
            
            self.blog.selectBlog(0)
            
            return True
            
    def refresh(self):
        gui.app.title = u"Wordmobi"
        gui.app.menu = [( u"Posts", (
                            ( u"Update", self.update ), 
                            ( u"New", self.new_post ),
                            ( u"Details", self.post_details ),
                            ( u"Delete", self.delete_post )
                            )),
                        ( u"Settings", self.config_wordmobi ),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]
        #               ( u"Categories", self.categories ),
        gui.app.body = self.body        
        gui.app.set_tabs( [], None )
        gui.app.exit_key_handler = self.close_app

    def close_app(self):
        self.lock.signal()

    def new_post(self):
        def cbk( param ):
            (title,contents,images,categories) = param
            if title is not None:
                self.connect()
                img_contents = ""
                
                for img in images:
                    img_src = self.blog.newMediaObject(img.encode('utf-8'))
                    img_contents = img_contents + \
                                   ("<img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" /><br>" % (img_src,img_src))
                    
                img_contents = img_contents + "<br><br>Posted by <a href=\"http://wordmobi.googlecode.com\">Wordmobi</a>"
                post = wp.WordPressPost()
                post.title = title.encode('utf-8')
                post.description = contents.encode('utf-8') + img_contents
                post.categories = [ self.blog.getCategoryIdFromName(c.encode('utf-8')) for c in categories ]
                post.allowComments = True
                
                try:
                    new_post = self.blog.newPost(post, True)
                except:
                    gui.note(u"Impossible to post to blog %s" % self.db["blog"],"info")
                    return
                
                gui.note(u"Published ! Update the post list","info")
            self.refresh()
            
        self.dlg = NewPost( cbk, blog_categories=self.cats )
        
        self.dlg.run()
        
    def update(self):
        self.connect()
        try:
            self.posts = self.blog.getRecentPostTitles( int(self.db["num_posts"]) )
        except:
            gui.note(u"Impossible to retrieve post titles list","info")
            return

        if len(self.posts) > 0:
            self.headlines = []
            for p in self. posts:
                months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                #timestamp = "%02d/%02d %02d:%02d " % (mo,d,h,m)
                timestamp = "%02d/%s " % (d,months[mo-1]) 
                self.headlines.append( self.unicode( timestamp + p['title'] ) )
        else:
            self.headlines = [ u"<empty>" ]
            gui.note( u"No posts available", "info" )

        try:
            cats = self.blog.getCategoryList()
        except:
            gui.note(u"Impossible to retrieve the categories list","info")
            return

        self.cats = [ decode_html(c.name) for c in cats ]        
        self.body.set_list( self.headlines )
        

    def list_comments(self):
        gui.app.title = u"wordmobi comments"
        gui.note( u"Comments cbk", "info" )
        gui.app.title = u"wordmobi Posts"

    def post_popup(self):
        idx = gui.popup_menu( [u"Details", u"Delete"], u"Posts")
        if idx is not None:
            [self.post_details , self.delete_post ][idx]()

    def delete_post(self):
        idx = self.body.current()
        if self.headlines[ idx ] == u"<empty>":
            gui.note( u"Please, update the post list", "info" )
            return

        ny = gui.popup_menu( [u"No", u"Yes"], u"Delete post ?" )
        if ny is not None:
            if ny == 1:
                self.connect()
                try:
                    self.blog.deletePost( self.posts[idx]['postid'] )
                except:
                    gui.note(u"Impossible to delete the post","info")
                    return
                gui.note(u"Post deleted","info")
        
    def post_details(self):
        idx = self.body.current()
        if self.headlines[ idx ] == u"<empty>":
            gui.note( u"Please, update the post list", "info" )
            return

        def cbk( p ):
            self.refresh()

        # if post was not totally retrieved yet, fetch all data
        self.connect()
        if self.posts[idx].has_key('description') == False:
            self.posts[idx] = self.blog.getPost( self.posts[idx]['postid'] )
            
        self.dlg = NewPost( cbk, \
                             self.unicode(self.posts[idx]['title']), \
                             self.unicode(self.posts[idx]['description']), \
                             self.cats,\
                             [ decode_html(c) for c in self.posts[idx]['categories'] ])
        self.dlg.run()


    def config_wordmobi(self):
        fields = [ (u"Blog","text",self.db["blog"]), \
                   (u"Posts","text",self.db["num_posts"]), \
                   (u"Username","text",self.db["user"]), \
                   (u"Password","text",self.db["pass"]) ]
        
        form = gui.Form(fields,gui.FFormEditModeOnly)
        form.menu = []
        form.save_hook = self.save_conf
        form.execute()

    def save_conf(self,conf):
        blog = conf[0][2]
        npst = conf[1][2]
        user = conf[2][2]
        pswd = conf[3][2]
        
        if not user or not pswd or not blog:
            gui.note(u"User, password and blog fields may not be blank","error")
            return

        try:
            np = int( npst )
        except:
            gui.note(u"Invalid value for number of posts","error")
            return

        if np < 1 or np > 100:
            gui.note(u"Please, select a number of post between 1 and 100","error")
            return

        self.db["user"] = user
        self.db["pass"] = pswd
        self.db["blog"] = blog
        self.db["num_posts"] = npst
        
        self.db.save()

    def about_wordmobi(self):
        def close_about():
            self.refresh()

        gui.app.exit_key_handler = close_about
        
        msg = u"""
Wordmobi, a client for Wordpress (%s)

Author: Marcelo Barros de Almeida
Email: marcelobarrosalmeida@gmail.com
Code: http://wordmobe.googlecode.com
Blog: http://wordmobi.wordpress.com
License: GNU GPLv3 (http://www.gnu.org/licenses/gpl-3.0.txt)

Use At Your Own Risk.
""" % VERSION
        
        about = gui.Text(msg)
        about.focus = False
        about.style = gui.STYLE_BOLD
        gui.app.body = about
        gui.app.menu = [ (u"Close", close_about )]
        
    def run(self):
        self.lock.wait()
        gui.app.set_tabs( [], None )

if __name__ == "__main__":

    wm = WordMobi()
    wm.run()

#['mt_keywords', 'permaLink', 'wp_slug', 'description', 'title',
#'post_status', 'date_created_gmt', 'mt_excerpt', 'userid', 'dateCreated',
#'custom_fields', 'wp_author_display_name', 'link', 'mt_text_more', 'mt_allow_comments',
#'wp_password', 'postid', 'wp_author_id', 'categories', 'mt_allow_pings']
