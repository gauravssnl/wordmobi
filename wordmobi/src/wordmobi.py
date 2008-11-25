# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32
import dt as datetime
from appuifw import *
import os
import wordpresslib as wp
import e32dbm
from persist import Persist
from newpost import NewPost
from editpost import EditPost
import re
from settings import Settings

__version__ = "0.1.5"

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
        self.headlines = [ (u"<empty>", u"Please, update the post list") ]        
        self.db = Persist()
        self.db.load()
        self.body = Listbox( self.headlines, self.post_popup )
        self.blog = None
        
        self.set_blog_url()
        self.refresh()

    def set_blog_url(self):
        blog = self.db["blog"] + "/xmlrpc.php"
        self.blog = wp.WordPressClient(blog, self.db["user"], self.db["pass"])
        self.blog.selectBlog(0)
            
    def refresh(self):
        app.title = u"Wordmobi"
        app.menu = [( u"Posts", (
                            ( u"Update", self.update ), 
                            ( u"New", self.new_post ),
                            ( u"Details", self.post_details ),
                            ( u"Delete", self.delete_post )
                            )),
                        ( u"Settings", self.config_wordmobi ),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]
        #               ( u"Categories", self.categories ),
        app.body = self.body        
        app.set_tabs( [], None )
        app.exit_key_handler = self.close_app

    def close_app(self):
        self.lock.signal()

    def new_post(self):
        def cbk( param ):
            if param[0] is not None:
                (title,contents,images,categories) = param
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
                    note(u"Impossible to post to blog %s" % self.db["blog"],"info")
                    return
                
                note(u"Published ! Update the post list","info")
            self.refresh()
            
        self.dlg = NewPost( cbk, blog_categories=self.cats )
        
        self.dlg.run()
        
    def update(self):
        try:
            self.posts = self.blog.getRecentPostTitles( int(self.db["num_posts"]) )
        except:
            note(u"Impossible to retrieve post titles list","info")
            return

        if len(self.posts) > 0:
            self.headlines = []
            for p in self. posts:
                months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                timestamp = u"%d/%s/%d  %02d:%02d:%02d" % (d,months[mo-1],y,h,m,s) 
                self.headlines.append( ( timestamp , self.unicode( p['title'] ) ) )
        else:
            self.headlines = [ (u"<empty>", u"Please, update the post list") ]
            note( u"No posts available", "info" )

        try:
            cats = self.blog.getCategoryList()
        except:
            note(u"Impossible to retrieve the categories list","info")
            return

        self.cats = [ decode_html(c.name) for c in cats ]        
        self.body.set_list( self.headlines )
        

    def list_comments(self):
        app.title = u"wordmobi comments"
        note( u"Comments cbk", "info" )
        app.title = u"wordmobi Posts"

    def post_popup(self):
        idx = popup_menu( [u"Details", u"Delete"], u"Posts")
        if idx is not None:
            [self.post_details , self.delete_post ][idx]()

    def delete_post(self):
        idx = self.body.current()
        if self.headlines[ idx ][0] == u"<empty>":
            note( u"Please, update the post list", "info" )
            return

        ny = popup_menu( [u"No", u"Yes"], u"Delete post ?" )
        if ny is not None:
            if ny == 1:
                try:
                    self.blog.deletePost( self.posts[idx]['postid'] )
                except:
                    note(u"Impossible to delete the post","info")
                    return
                note(u"Post deleted","info")
        
    def post_details(self):
        idx = self.body.current()
        if self.headlines[ idx ][0] == u"<empty>":
            note( u"Please, update the post list", "info" )
            return

        def cbk( p ):
            self.refresh()

        # if post was not totally retrieved yet, fetch all data
        if self.posts[idx].has_key('description') == False:
            self.posts[idx] = self.blog.getPost( self.posts[idx]['postid'] )
            
        self.dlg = NewPost( cbk, \
                             self.unicode(self.posts[idx]['title']), \
                             self.unicode(self.posts[idx]['description']), \
                             self.cats,\
                             [ decode_html(c) for c in self.posts[idx]['categories'] ])
        self.dlg.run()


    def config_wordmobi(self):
        def cbk( params ):
            if params[0] is not None:
                (self.db["blog"], self.db["user"], self.db["pass"], np) = params
                self.db["num_posts"] = unicode( np )
                self.db.save()
                self.set_blog_url()
            self.refresh()
            
        self.dlg = Settings( cbk,self.db["blog"], self.db["user"], self.db["pass"], int(self.db["num_posts"]) )
        self.dlg.run()           
        
    def about_wordmobi(self):
        def close_about():
            self.refresh()
        app.title = u"About"
        app.exit_key_handler = close_about
        about = [ ( u"Wordmobi %s" % __version__, u"A Wordpress client" ),\
                  ( u"Author", u"Marcelo Barros de Almeida"), \
                  ( u"Email", u"marcelobarrosalmeida@gmail.com"), \
                  ( u"Source code", u"http://wordmobi.googlecode.com"), \
                  ( u"Blog", u"http://wordmobi.wordpress.com"), \
                  ( u"License", u"GNU GPLv3"), \
                  ( u"Warning", u"Use at your own risk") ]
        app.body = Listbox( about, lambda: None )
        app.menu = [ (u"Close", close_about )]
 
    def run(self):
        old_title = app.title
        self.lock.wait()
        app.set_tabs( [], None )
        app.title = old_title
        app.menu = []
        app.body = None
        app.set_exit()


if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
