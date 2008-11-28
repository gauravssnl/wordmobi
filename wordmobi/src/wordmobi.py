# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32, e32dbm
import dt as datetime
from appuifw import *
import os
import topwindow, graphics
import wordpresslib as wp
from persist import Persist
from newpost import NewPost
from editpost import EditPost
from settings import Settings
from wmutil import *
from viewcomments import ViewComments

__version__ = "0.2.2"

PROMO_PHRASE = "<br><br>Posted by <a href=\"http://wordmobi.googlecode.com\">Wordmobi</a>"
        
class WordMobi(object):
    def __init__(self):
        self.lock = e32.Ao_lock()
        self.ui_lock = False
        self.app_title = u"Wordmobi"
        self.cats = [u"Uncategorized"]
        self.headlines = []
        self.posts = []        
        self.db = Persist()
        self.db.load()
        self.body = Listbox( [(u"",u"")], self.post_popup_check_lock )
        self.blog = None
        self.dlg = None
        self.menu = [( u"Posts", (
                            ( u"Update", self.update ), 
                            ( u"Contents", self.post_contents ),
                            ( u"Comments", self.post_comments ),
                            ( u"Delete", self.delete_post ),
                            ( u"New", self.new_post ),
                            )),
                        ( u"Settings", self.config_wordmobi ),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]     
        self.set_blog_url()
        self.refresh()

    def set_blog_url(self):
        blog = self.db["blog"] + "/xmlrpc.php"
        self.blog = wp.WordPressClient(blog, self.db["user"], self.db["pass"])
        self.blog.selectBlog(0)
            
    def refresh(self):
        app.title = self.app_title
        app.menu = self.menu
        if len( self.headlines ) == 0:
            self.headlines = [ (u"<empty>", u"Please, update the post list") ]
            self.posts = []
        self.body.set_list( self.headlines )
        app.body = self.body        
        app.set_tabs( [], None )
        app.exit_key_handler = self.close_app

    def lock_ui(self,msg = u""):
        self.ui_lock = True
        app.menu = []
        if msg:
            app.title = msg

    def unlock_ui(self):
        self.ui_lock = False
        app.menu = self.menu
        app.title = self.app_title

    def ui_is_locked(self):
        return self.ui_lock
    
    def close_app(self):
        self.lock.signal()

    def new_post_cbk( self, params ):
        if params[0] is not None:
            (title,contents,images,categories) = params
            more_contents = ""
            m = len(images)
            for n in range(m):
                fname = images[n].encode('utf-8')
                self.lock_ui( u"Uploading (%d/%d) %s..." % (n+1,m,os.path.basename(fname)) )
                try:
                    img_src = self.blog.newMediaObject(fname)
                except:
                    note(u"Impossible to upload %s. Try again." % fname,"error")
                    self.unlock_ui()
                    return False
                more_contents = more_contents + \
                               ("<img border=\"0\" class=\"aligncenter\" src=\"%s\" alt=\"%s\" /><br>" % (img_src,os.path.basename(fname)))
                
            self.lock_ui( u"Uploading post contents..." )
            more_contents = more_contents + PROMO_PHRASE
            post = wp.WordPressPost()
            post.title = title.encode('utf-8')
            post.description = contents.encode('utf-8') + more_contents
            post.categories = [ self.blog.getCategoryIdFromName(c.encode('utf-8')) for c in categories ]
            post.allowComments = True
            
            try:
                npost = self.blog.newPost(post, True)
            except:
                note(u"Impossible to post. Try again.","error")
                self.unlock_ui()
                return False

            self.lock_ui( u"Updating post list..." )
            try:
                p = self.blog.getLastPostTitle( )                
            except:
                note(u"Impossible to update post title. Try again.","error")
                self.unlock_ui() 
                self.refresh()
                return True
            
            if self.headlines[0][0] == u"<empty>":
                self.headlines = []
                self.posts = []
  
            (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
            timestamp = u"%d/%s/%d  %02d:%02d:%02d" % (d,MONTHS[mo-1],y,h,m,s) 
            self.headlines.insert( 0, ( timestamp , utf8_to_unicode( p['title'] ) ) )
            self.posts.insert( 0, p )
            
        self.unlock_ui()   
        self.refresh()
        return True
        
    def new_post(self):
        self.dlg = NewPost( self.new_post_cbk, u"", u"", self.cats, [], [] )
        self.dlg.run()
                 
    def update(self):
        self.lock_ui(u"Downloading posts..." )
        try:
            self.posts = self.blog.getRecentPostTitles( int(self.db["num_posts"]) )
        except:
            note(u"Impossible to retrieve post titles.","error")
            self.unlock_ui()
            return
        
        if len(self.posts) > 0:
            self.headlines = []
            for p in self.posts:
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                line1 = u"%d/%s/%d  %02d:%02d:%02d" % (d,MONTHS[mo-1],y,h,m,s)
                line2 = utf8_to_unicode( p['title'] )
                self.headlines.append( ( line1 , line2 ) )
        else:
            self.headlines = []
            note( u"No posts available.", "info" )

        self.lock_ui(u"Downloading categories...")
        try:
            cats = self.blog.getCategoryList()
        except:
            note(u"Impossible to retrieve the categories list.","error")
            self.unlock_ui()
            return

        self.cats = [ decode_html(c.name) for c in cats ]
        self.unlock_ui()
        self.refresh()
        
    def list_comments(self):
        app.title = u"wordmobi comments"
        note( u"Comments cbk", "info" )
        app.title = u"wordmobi Posts"

    def post_popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.post_popup()
            
    def post_popup(self):
        idx = popup_menu( [u"Contents", u"Comments",u"Delete",u"Update"], u"Posts")
        if idx is not None:
            [self.post_contents , self.post_comments, self.delete_post, self.update ][idx]()

    def delete_post(self):
        idx = self.body.current()
        if self.headlines[idx][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return

        ny = popup_menu( [u"No", u"Yes"], u"Delete post ?" )
        if ny is not None:
            if ny == 1:
                self.lock_ui(u"Deleting post...")
                try:
                    self.blog.deletePost( self.posts[idx]['postid'] )
                except:
                    self.unlock_ui()
                    note(u"Impossible to delete the post.","error")
                    return
                self.headlines = self.headlines[:idx] + self.headlines[idx+1:]
                self.posts = self.posts[:idx] + self.posts[idx+1:]
                note(u"Post deleted.","info")
                self.unlock_ui() 
                self.refresh()

    def post_contents_cbk(self,params):
        self.refresh()
        return True
        
    def post_contents(self):
        idx = self.body.current()
        if self.headlines[idx][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return
        
        # if post was not totally retrieved yet, fetch all data
        if self.posts[idx].has_key('description') == False:
            self.lock_ui(u"Downloading post...")
            try:
                self.posts[idx] = self.blog.getPost( self.posts[idx]['postid'] )
            except:
                self.unlock_ui()
                note(u"Impossible to download the post. Try again.","error")
                return
            self.unlock_ui() 
                        
        self.dlg = NewPost( self.post_contents_cbk, \
                             utf8_to_unicode(self.posts[idx]['title']), \
                             utf8_to_unicode(self.posts[idx]['description']), \
                             self.cats,\
                             [ decode_html(c) for c in self.posts[idx]['categories'] ], \
                            [])
        self.dlg.run()

    def post_comments_cbk(self):
        self.refresh()
        return True

    def post_comments(self):
        idx = self.body.current()
        if self.headlines[idx][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return
        
        # if post was not totally retrieved yet, fetch all data
        if self.posts[idx].has_key('comments') == False:
            self.lock_ui(u"Downloading comments...")
            comm_info = wp.WordPressComment()
            comm_info.post_id = self.posts[idx]['postid']
            comm_info.number = self.db['num_comments']
            try:
                self.posts[idx]['comments'] = self.blog.getComments( comm_info )
            except:
                self.unlock_ui()
                note(u"Impossible to download comments. Try again.","error")
                return
            self.unlock_ui() 

        nc = len( self.posts[idx]['comments'] )
        if nc == 0:
            note(u"No comments for this post.","info")
        else:
            self.dlg = ViewComments( self.post_comments_cbk, \
                                     self.posts[idx]['comments'], \
                                     utf8_to_unicode(self.posts[idx]['title']))
            self.dlg.run()
            
    def config_wordmobi_cbk(self,params):
        if params[0] is not None:
            (self.db["blog"], self.db["user"], self.db["pass"], np, nc) = params
            self.db["num_posts"] = unicode( np )
            self.db["num_comments"] = unicode( nc )
            self.db.save()
            self.set_blog_url()
        self.refresh()
            
    def config_wordmobi(self):
        self.dlg = Settings( self.config_wordmobi_cbk,\
                             self.db["blog"], \
                             self.db["user"], self.db["pass"], \
                             int(self.db["num_posts"]), \
                             int(self.db["num_comments"]) )
        self.dlg.run()
        
    def about_wordmobi(self):
        app.title = u"About"
        app.exit_key_handler = lambda: self.refresh()
        about = [ ( u"Wordmobi %s" % __version__, u"A Wordpress client" ),\
                  ( u"Author", u"Marcelo Barros de Almeida"), \
                  ( u"Email", u"marcelobarrosalmeida@gmail.com"), \
                  ( u"Source code", u"http://wordmobi.googlecode.com"), \
                  ( u"Blog", u"http://wordmobi.wordpress.com"), \
                  ( u"License", u"GNU GPLv3"), \
                  ( u"Warning", u"Use at your own risk") ]
        app.body = Listbox( about, lambda: None )
        app.menu = [ (u"Close", lambda: self.refresh() )]
 
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
