import os
from appuifw import *
from window import Application
from about import About
from settings import Settings, sel_access_point
from posts import Posts
from comments import Comments
from categories import Categories
import wordpresslib as wp
import e32, e32dbm
from wmutil import *
from wmproxy import UrllibTransport
import urllib, time
from beautifulsoup import BeautifulSoup
import key_codes

VERSION = "0.4.0"

__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = VERSION
__copyright__ = "Copyright (c) 2008- Marcelo Barros de Almeida"
__license__ = "GPLv3"

PROMO_PHRASE = "<br><br>Posted by <a href=\"http://wordmobi.googlecode.com\">Wordmobi</a>"
DEFDIR = "e:\\wordmobi\\"

DB  = None
BLOG = None

class Persist(dict):
    __highlander = None
    DBNAME = os.path.join(DEFDIR,"wordmobi")
    DEFVALS = {"user":u"username",
               "pass":u"password",
               "blog":u"http://blogname.wordpress.com",
               "email":u"",
               "realname":u"",
               "num_posts":u"10",
               "num_comments":u"20",
               "categories":u"",
               "proxy_user":u"",
               "proxy_pass":u"",
               "proxy_addr":u"",
               "proxy_port":u"8080",
               "proxy_enabled":u"False"}
    
    def __init__(self):
        if Persist.__highlander:
            raise Persist.__highlander
        Persist.__highlander = self
        
        dict.__init__(self)
        
        self.load()
            
    def save(self):
        db = e32dbm.open(Persist.DBNAME,"c")
        for k in Persist.DEFVALS.iterkeys():
            db[k] = self.__getitem__(k)
        db.close()

    def load(self):
        try:
            db = e32dbm.open(Persist.DBNAME,"w")
        except:
            db = e32dbm.open(Persist.DBNAME,"n")
            
        for k in Persist.DEFVALS.iterkeys():
            try:
                self.__setitem__(k,utf8_to_unicode( db[k] ))
            except:
                self.__setitem__(k,Persist.DEFVALS[k])
        db.close()

class WordPressWrapper(object):

    __highlander = None

    def __init__(self):
        if WordPressWrapper.__highlander:
            raise WordPressWrapper.__highlander
        WordPressWrapper.__highlander = self

        self.posts = []
        self.comments = []
        self.categories = [ { 'categoryName':u"Uncategorized", 'categoryId':'1', 'parentId':'0' } ]    
        self.blog = None

    def categoryNamesList(self):
        return map( lambda x:  x['categoryName'] , self.categories)

    def categoryName2Id(self,cat):
        for c in self.categories:
            if c['categoryName'] == cat:
                return (c['categoryId'], c['parentId'])
            
    def update_categories(self):
        """ Update categories. Return True or False.
        """
        try:
            self.categories = self.blog.getCategories()
        except:
            note(u"Impossible to retrieve the categories list.","error")
            return False

        for i in range(len(self.categories)):
            # WP may return html with scape codes like &#nn;
            # or utf-8, when ascii can not represent accents.
            # so, the only way I found to make this work is below:
            try:
                self.categories[i]['categoryName'] = decode_html( self.categories[i]['categoryName'] )
            except:
                self.categories[i]['categoryName'] = utf8_to_unicode( self.categories[i]['categoryName'] )

        # categories *never* may be empty
        if len( self.categories ) == 0:
            self.categories = [ { 'categoryName':u"Uncategorized", 'categoryId':'1', 'parentId':'0' } ]
            
        return True

    def delete_category(self, item):
        retval = False
        cat_id = self.categories[item]['categoryId']
        cat_name = self.categories[item]['categoryName']
        
        try:
            res = self.blog.deleteCategory(cat_id)
        except:
            note(u"Impossible to delete category %s." % cat_name,"error")
            
        if res == True:
            del self.categories[item]
            note(u"Category %s deleted." % cat_name,"info")
            retval = True
        else:
            note(u"Impossible to delete category %s." % cat_name,"error")

        # categories *never* may be empty
        if len( self.categories ) == 0:
            self.categories = [ { 'categoryName':u"Uncategorized", 'categoryId':'1', 'parentId':'0' } ]
            
        return retval

    def new_category(self,cat_name):
        wpc = wp.WordPressNewCategory()
        wpc.name = unicode_to_utf8( cat_name )
        wpc.slug=''
        wpc.parent_id = 0
        wpc.description = unicode_to_utf8( cat_name )
        cat_id = None
        try:
            cat_id = self.blog.newCategory(wpc)
        except:
            note(u"Impossible to create category %s." % cat_name,"error")
            return False
        return True

    def update_posts(self):
        try:
            self.posts = self.blog.getRecentPostTitles( int(DB["num_posts"]) )
        except:
            note(u"Impossible to update posts.","error")
            return False
        return True

    def get_post(self,item):
        try:
            self.posts[item] = self.blog.getPost( self.posts[item]['postid'] )
        except:
            note(u"Impossible to download the post. Try again.","error")
            return False
        
        return True

    def upload_images(self, fname):
        app.title = u"Uploading %s..." % ( os.path.basename(fname) ) 
        try:
            img_src = self.blog.newMediaObject(fname)
        except:
            note(u"Impossible to upload %s. Try again." % fname,"error")
            return None
        
        return img_src
    
    def upload_new_post(self, title, contents, categories, publish):
        """ Uplaod a new post
        """
        app.title = u"Uploading post contents..." 
                      
        soup = BeautifulSoup( unicode_to_utf8(contents) )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n","")
        app.title = u"Uploading post contents..." 

        post = wp.WordPressPost()
        post.description = contents + PROMO_PHRASE
                      
        post.title = unicode_to_utf8( title )
        post.categories = [ self.categoryName2Id(c)[0] for c in categories ]
        post.allowComments = True

        try:
            npost = self.blog.newPost(post, publish)
        except:
            note(u"Impossible to publish the post. Try again.","error")
            npost = -1

        if npost >= 0:
            app.title =  u"Updating post list..." 
            try:
                p = self.blog.getLastPostTitle( )
                self.posts.insert( 0, p )
            except:
                note(u"Impossible to update post title. Try again.","error")

        return npost

    def edit_post(self, title, contents, categories, post_orig, publish):
        app.title = u"Uploading post contents..."

        soup = BeautifulSoup( unicode_to_utf8(contents) )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n","")
        app.title = u"Uploading post contents..."

        post = wp.WordPressPost()
        post.id = post_orig['postid']
        post.title = unicode_to_utf8( title )
        post.description = contents
        post.categories = [ self.categoryName2Id(c)[0] for c in categories ]
        post.allowComments = True
        post.permaLink = post_orig['permaLink']
        post.textMore = post_orig['mt_text_more']
        post.excerpt = post_orig['mt_excerpt']

        ret = True
        try:
            npost = self.blog.editPost( post.id, post, publish)
        except:
            note(u"Impossible to update the post. Try again.","error")
            ret = False

        upd_ok = False
        if ret:
            app.title = u"Uploading post list..."
            try:
                upd_post = self.blog.getPost(post.id)
                upd_ok = True
            except:
                note(u"Impossible to update post title. Try again.","error")

        if upd_ok:
            # update the list !
            for idx in range(len(self.posts)):
                if self.posts[idx]['postid'] == post.id:
                    self.posts[idx] = upd_post
                    break

        return ret
        
    def set_blog(self):
        if DB["proxy_enabled"] == u"True":
            user = unicode_to_utf8( DB["proxy_user"] )
            addr = unicode_to_utf8( DB["proxy_addr"] )
            port = unicode_to_utf8( DB["proxy_port"] )
            user = unicode_to_utf8( DB["proxy_user"] )
            pwrd = unicode_to_utf8( DB["proxy_pass"] )
            
            if len(user) > 0:
                proxy = "http://%s:%s@%s:%s" % (user,pwrd,addr,port)
            else:
                proxy = "http://%s:%s" % (addr,port)
                
            transp = UrllibTransport()
            transp.set_proxy(proxy)
            os.environ["http_proxy"] = proxy # for urllib
        else:
            transp = None
            os.environ["http_proxy"] = {}
            del os.environ["http_proxy"]
            
        blog_url = unicode_to_utf8( DB["blog"] ) + "/xmlrpc.php"
        self.blog = wp.WordPressClient(blog_url, unicode_to_utf8( DB["user"] ), unicode_to_utf8( DB["pass"] ), transp)
        self.blog.selectBlog(0)
        
class WordMobi(Application):
    
    def __init__(self):

        global DB, BLOG
        
        items = [ ( u"Posts", u"" ),
                  ( u"Comments", u"" ),
                  ( u"Categories", u"" ),
                  ( u"Settings", u"" ),
                  ( u"Upgrade", u"" ),
                  ( u"About", u"" )]
        
        Application.__init__(self,  u"Wordmobi", Listbox( items, self.check_update_value ))

        self.dlg = None
        
        self.check_dirs()
        DB = Persist()
        DB.load()
        BLOG = WordPressWrapper()
        sel_access_point()
        BLOG.set_blog()

        self.bind(key_codes.EKeyRightArrow, self.check_update_value)
        self.bind(key_codes.EKeyLeftArrow, self.close)
        
    def check_dirs(self):
        dirs = (DEFDIR,
                os.path.join(DEFDIR,"cache"),
                os.path.join(DEFDIR,"images"),
                os.path.join(DEFDIR,"updates"))
        for d in dirs:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except:
                    note(u"Could't create directory %s" % d,"error")

    def check_update_value(self):
        if not self.ui_is_locked():
            self.update_value()
            
    def update_value(self):
        idx = self.body.current()
        ( self.posts, self.comments, self.categories, self.settings, self.upgrade, self.about)[idx]()

    def default_cbk(self):
        #self.unlock_ui()
        self.refresh()
        return True
    
    def posts(self):
        self.dlg = Posts(self.default_cbk)
        self.dlg.run()

    def comments(self):
        self.dlg = Comments(self.default_cbk)
        self.dlg.run()

    def categories(self):
        self.dlg = Categories(self.default_cbk)
        self.dlg.run()
        
    def settings(self):
        self.dlg = Settings(self.default_cbk)
        self.dlg.run()

    def upgrade(self):
        if DB["proxy_enabled"] == u"True" and len(DB["proxy_user"]) > 0:
            note(u"Proxy authentication not supported for this feature","info")
            return

        self.lock_ui(u"Checking update page...")
        
        url = "http://code.google.com/p/wordmobi/wiki/LatestVersion"
        local_file = "web_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        local_file = os.path.join(DEFDIR, "cache", local_file)

        #title = self.get_title() 
        #self.set_title( u"Checking update page..." )
        ok = True
        try:
            urllib.urlretrieve( url, local_file )
        except:
            note(u"Impossible to access update page %s" % url,"error")
            ok = False

        if ok:
            html = open(local_file).read()
            soup = BeautifulSoup( html )
            addrs = soup.findAll('a')
            version = ""
            file_url = ""
            for addr in addrs:
                if addr.contents[0] == "latest_wordmobi_version":
                    version = addr["href"]
                elif addr.contents[0] == "wordmobi_sis_url":
                    file_url = addr["href"]

            if version and file_url:
                version = version[version.rfind("/")+1:]
                yn = popup_menu( [ u"Yes", u"No"], "Download %s ?" % (version) )
                if yn is not None:
                    if yn == 0:
                        sis_name = file_url[file_url.rfind("/")+1:]
                        local_file = os.path.join(DEFDIR, "updates", sis_name)

                        self.set_title( u"Downloading ..." )
                        ok = True
                        try:
                            urllib.urlretrieve( file_url, local_file )
                        except:
                            note(u"Impossible to download %s" % sis_name, "error")
                            ok = False

                        if ok:
                            note(u"%s downloaded in e:\\wordmobi\\updates. Please, install it." % sis_name, "info")

            else:
                note(u"Upgrade information missing.","error")
                
        self.set_title( u"Wordmobi" )
        self.unlock_ui()
        self.refresh()

    def close(self):
        ny = popup_menu( [u"Yes", u"No"], u"Exit ?" )
        if ny is not None:
            if ny == 0:
                self.clear_cache()
                Application.close(self)

    def clear_cache(self):
        not_all = False
        cache = os.path.join(DEFDIR, "cache")
        entries = os.listdir( cache )
        for e in entries:
            fname = os.path.join(cache,e)
            if os.path.isfile( fname ):
                try:
                    os.remove( fname )
                except:
                    not_all = True
        if not_all:
            note(u"Not all files in %s could be removed. Try to remove them later." % cache,"error")
            
    def about(self):
        self.dlg = About(self.default_cbk)
        self.dlg.run()
        
if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
