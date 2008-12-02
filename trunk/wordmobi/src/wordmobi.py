# -*- coding: utf-8 -*-
import sys
sys.path.append("e:\\python")
import e32, e32dbm
import datetime
from appuifw import *
import os
import topwindow, graphics
import wordpresslib as wp
from persist import Persist
from posts import NewPost, EditPost
from settings import *
from wmutil import *
from viewcomments import ViewComments
from wmproxy import UrllibTransport
from socket import select_access_point, access_point, access_points, set_default_access_point
from beautifulsoup import BeautifulSoup

__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = "0.2.6"
__copyright__ = "Copyright (c) 2008- Marcelo Barros de Almeida"
__license__ = "GPLv3"

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
                            ( u"New", self.new_post )
                            )),
                        ( u"Settings", (
                            ( u"Blog access", self.config_wordmobi ),
                            ( u"Proxy",self.config_network ),
                            ( u"Access Point", self.sel_access_point )
                            )),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]
        self.sel_access_point()
        self.refresh()

    def sel_access_point(self):
        aps = access_points()
        if len(aps) == 0:
            note(u"Could't find any access point.","error")
            return False
        
        ap_labels = map( lambda x: x['name'], aps )
        item = popup_menu( ap_labels, u"Access points:" )
        if item == None:
            note(u"At least one access point is required.","error")
            return False
        
        apo = access_point(aps[item]['iapid'])
        self.def_ap = { 'apo': apo, 'name': aps[item]['name'], 'apid': aps[item]['iapid'] }
        set_default_access_point(self.def_ap['apo'])

        self.set_blog_url()
        
        return True
        
    def set_blog_url(self):
        if self.db["proxy_enabled"] == u"True":
            user = self.db["proxy_user"].encode('utf-8')
            addr = self.db["proxy_addr"].encode('utf-8')
            port = self.db["proxy_port"].encode('utf-8')
            user = self.db["proxy_user"].encode('utf-8')
            pwd = self.db["proxy_pass"].encode('utf-8')
            
            if len(user) > 0:
                proxy = "http://%s:%s@%s:%s" % (user,pwd,addr,port)
            else:
                proxy = "http://%s:%s" % (addr,port)
                
            transp = UrllibTransport()
            transp.set_proxy(proxy)
            os.environ["http_proxy"] = proxy # for urllib
        else:
            transp = None
            os.environ["http_proxy"] = {}
            del os.environ["http_proxy"]
            
        blog = self.db["blog"].encode('utf-8') + "/xmlrpc.php"
        del self.blog
        self.blog = wp.WordPressClient(blog, self.db["user"].encode('utf-8'), self.db["pass"].encode('utf-8'),transp)
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

    def upload_images(self, fname):
        self.lock_ui( u"Uploading %s..." % ( os.path.basename(fname) ) )
        try:
            img_src = self.blog.newMediaObject(fname)
        except:
            note(u"Impossible to upload %s. Try again." % fname,"error")
            return None
        
        return img_src

    def upload_new_post(self, title, contents, categories):
        """ Uplaod a new or edited post. For new post, use post_id as None
        """
        self.lock_ui( u"Uploading post contents...")
                      
        soup = BeautifulSoup( contents.encode('utf-8') )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n","")
        self.lock_ui( u"Uploading post contents..." )

        post = wp.WordPressPost()
        post.description = contents + PROMO_PHRASE
                      
        post.title = title.encode('utf-8')
        post.categories = [ self.blog.getCategoryIdFromName(c.encode('utf-8')) for c in categories ]
        post.allowComments = True

        try:
            npost = self.blog.newPost(post, True)
        except:
            note(u"Impossible to post. Try again.","error")
            raise

        return npost
    
    def new_post_cbk( self, params ):
        if params is not None:
            (title,contents,categories) = params

            try:
                self.upload_new_post(title, contents, categories)
            except:
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
        self.dlg = NewPost( self.new_post_cbk, u"", u"", self.cats, [] )
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
        if params is not None:
            (title,contents,categories,post_orig) = params

            self.lock_ui( u"Uploading post contents...")

            soup = BeautifulSoup( contents.encode('utf-8') )
            for img in soup.findAll('img'):
                if os.path.isfile( img['src'] ): # just upload local files
                    url = self.upload_images( img['src'] )
                    if url is not None:
                        img['src'] = url

            contents = soup.prettify().replace("\n","")

            post = wp.WordPressPost()
            post.id = post_orig['postid']
            post.title = title.encode('utf-8')
            post.description = contents
            post.categories = [ self.blog.getCategoryIdFromName(c.encode('utf-8')) for c in categories ]
            post.allowComments = True
            post.permaLink = post_orig['permaLink']
            post.textMore = post_orig['mt_text_more']
            post.excerpt = post_orig['mt_excerpt']

            try:
                npost = self.blog.editPost( post.id, post, True)
            except:
                note(u"Impossible to update the post. Try again.","error")
                self.unlock_ui()
                return False

            try:
                upd_post = self.blog.getPost(post.id)
            except:
                note(u"Impossible to update post title. Try again.","error")

            # update the list !
            for idx in range(len(self.posts)):
                if self.posts[idx]['postid'] == post.id:
                    ( line1 , line2 ) = self.headlines[idx]
                    line2 = utf8_to_unicode( post.title )
                    self.headlines[idx] = ( line1 , line2 )
                    del self.posts[idx]['description'] # force reload
                    break
    
        self.unlock_ui()   
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
                        
        self.dlg = EditPost( self.post_contents_cbk, self.cats, self.posts[idx] )
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
        if params is not None:
            (self.db["blog"], self.db["user"], self.db["pass"], np, nc) = params
            self.db["num_posts"] = unicode( np )
            self.db["num_comments"] = unicode( nc )
            self.db.save()
            self.set_blog_url()
        self.refresh()
        return True
            
    def config_wordmobi(self):
        self.dlg = BlogSettings( self.config_wordmobi_cbk,\
                                 self.db["blog"], \
                                 self.db["user"], self.db["pass"], \
                                 int(self.db["num_posts"]), \
                                 int(self.db["num_comments"]) )
        self.dlg.run()

    def config_network_cbk(self,params):
        if params is not None:
            (self.db["proxy_enabled"],self.db["proxy_addr"],port,self.db["proxy_user"],self.db["proxy_pass"]) = params
            self.db["proxy_port"] = unicode( port )
            self.db.save()
            self.set_blog_url()
        self.refresh()
        return True
    
    def config_network(self):
        self.dlg = ProxySettings( self.config_network_cbk,\
                                  self.db["proxy_enabled"], \
                                  self.db["proxy_addr"], \
                                  int(self.db["proxy_port"]), \
                                  self.db["proxy_user"], \
                                  self.db["proxy_pass"])
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
