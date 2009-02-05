import os
import time
import urllib
from beautifulsoup import BeautifulSoup
from xmlrpclib import DateTime
from appuifw import *
import wordpresslib as wp
from wmutil import *
from wmproxy import UrllibTransport
from persist import DB
from wmglobals import PROMO_PHRASE
from wmlocale import LABELS

__all__ = [ "WordPressWrapper", "BLOG" ]

class WordPressWrapper(object):
    def __init__(self):
        self.posts = []
        self.comments = []
        self.categories = []
        self.cat_default = []
        self.refresh()
        self.categories = self.cat_default   
        self.blog = None
        
    def refresh(self):
        """ Update variables related to multiple idioms support
        """
        # just use default values if categories were not retrieved yet
        if self.categories == self.cat_default:
            self.categories = []
        self.cat_default = [ { 'categoryName':LABELS.loc.wp_list_uncategorized,
                               'categoryId':'1',
                               'parentId':'0' } ]
        if not self.categories:
            self.categories = self.cat_default
        
    def categoryNamesList(self):
        return map( lambda x:  x['categoryName'] , self.categories)

    def categoryName2Id(self,cat):
        for c in self.categories:
            if c['categoryName'] == cat:
                return (c['categoryId'], c['parentId'])
        return ( '0', '0' )
            
    def update_categories(self):
        """ Update categories. Return True or False.
        """
        try:
            self.categories = self.blog.getCategories()
        except:
            note(LABELS.loc.wp_err_cant_downl_cat,"error")
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
        if not self.categories:
            self.categories = self.cat_default
            
        return True

    def delete_category(self, item):
        retval = False
        cat_id = self.categories[item]['categoryId']
        cat_name = self.categories[item]['categoryName']
        
        try:
            res = self.blog.deleteCategory(cat_id)
        except:
            note(LABEL.loc.wp_err_cant_del_cat % cat_name,"error")
            
        if res:
            del self.categories[item]
            note(LABELS.loc.wp_info_cat_del % cat_name,"info")
            retval = True
        else:
            note(LABEL.loc.wp_err_cant_del_cat % cat_name,"error")

        # categories *never* may be empty
        if not self.categories:
            self.categories = self.cat_default
            
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
            note(LABELS.loc.wp_err_cant_create_cat % cat_name,"error")
            return False
        return True

    def update_posts(self):
        try:
            self.posts = self.blog.getRecentPostTitles( int(DB["num_posts"]) )
        except:
            note(LABELS.loc.wp_err_cant_updt_post,"error")
            return False

        return self.update_categories()

    def get_post(self,item):
        try:
            self.posts[item] = self.blog.getPost( self.posts[item]['postid'] )
        except:
            note(LABELS.loc.wp_err_cant_downl_post,"error")
            return False
        
        return True

    def upload_images(self, fname):
        app.title = LABELS.loc.wp_info_upld_img % ( os.path.basename(fname) ) 
        try:
            img_src = self.blog.newMediaObject(fname)
        except:
            note(LABELS.loc.wp_err_cant_upld_img % fname,"error")
            return None
        
        return img_src
    
    def new_post(self, title, contents, categories, publish):
        """ Uplaod a new post
        """
        app.title = LABELS.loc.wp_info_upld_post_cont
                      
        soup = BeautifulSoup( unicode_to_utf8(contents) )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n"," ")
        app.title = LABELS.loc.wp_info_upld_post_cont 

        post = wp.WordPressPost()
        post.description = contents + PROMO_PHRASE
                      
        post.title = unicode_to_utf8( title )
        post.categories = [ self.categoryName2Id(c)[0] for c in categories ]
        post.allowComments = True

        try:
            npost = self.blog.newPost(post, publish)
        except:
            note(LABELS.loc.wp_err_cant_pub_post,"error")
            npost = -1

        if npost >= 0:
            app.title =  LABELS.loc.wp_info_updt_post_list 
            try:
                p = self.blog.getLastPostTitle( )
                self.posts.insert( 0, p )
            except:
                note(LABELS.loc.wp_err_cant_updt_post_list,"error")

        return npost

    def edit_post(self, title, contents, categories, post_orig, publish):
        app.title = LABELS.loc.wp_info_upld_post_cont

        soup = BeautifulSoup( unicode_to_utf8(contents) )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n"," ")
        app.title = LABELS.loc.wp_info_upld_post_cont

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
            note(LABELS.loc.wp_err_cant_updt_the_post,"error")
            ret = False

        upd_ok = False
        if ret:
            app.title = LABELS.loc.wp_info_updt_post_list
            try:
                upd_post = self.blog.getPost(post.id)
                upd_ok = True
            except:
                note(LABELS.loc.wp_err_cant_updt_post_list,"error")

        if upd_ok:
            # update the list !
            for idx in range(len(self.posts)):
                if self.posts[idx]['postid'] == post.id:
                    self.posts[idx] = upd_post
                    break

        return ret

    def delete_post(self, idx):
        try:
            self.blog.deletePost(self.posts[idx]['postid'])
        except:
            return False
        
        del self.posts[idx]
        return True


    def get_comment(self, post_idx, comment_status):
        post_id = self.posts[post_idx]['postid']
        comm_info = wp.WordPressComment()
        comm_info.post_id = post_id
        comm_info.status = comment_status
        comm_info.number = DB['num_comments']
        try:
            comments = self.blog.getComments( comm_info )
        except:
            note(LABELS.loc.wp_err_cant_downl_cmt,"error")
            return False

        self.comments = self.comments + comments
        
        return True

    def edit_comment(self, idx, email, realname, website, contents):
        
        comment_id = self.comments[idx]['comment_id']
        comment = wp.WordPressEditComment()
        comment.status = 'approve'
        comment.content = unicode_to_utf8( contents )
        comment.author = unicode_to_utf8( realname )
        comment.author_url = unicode_to_utf8( website )
        comment.author_email = unicode_to_utf8( email )
        comment.date_created_gmt = DateTime( time.mktime(time.gmtime()) ) # gmt time required
    
        try:
            self.blog.editComment(comment_id, comment)
        except:
            note(LABELS.loc.wp_err_cant_updt_cmt,"error")
            return False

        try:
            c = self.blog.getComment( comment_id )
        except:
            note(LABELS.loc.wp_err_cant_updt_cmt_list,"error")
            c = None

        if c:
            self.comments[idx] = c

        return True

    def new_comment(self, post_id, email, realname, website, contents):

        comment = wp.WordPressNewComment()
        comment.status = 'approve'
        comment.content = unicode_to_utf8( contents )
        comment.author = unicode_to_utf8( realname )
        comment.author_url = unicode_to_utf8( website )
        comment.author_email = unicode_to_utf8( email )

        try:
            comment_id = self.blog.newComment( post_id, comment )
        except:
            note(LABELS.loc.wp_err_cant_pub_cmt,"error")
            return False

        try:
            c = self.blog.getComment( comment_id )
        except:
            note(LABELS.loc.wp_err_cant_updt_cmt_list,"error")
            c = None

        if c:
            self.comments.insert(0,c)
        
        return True

    def approve_comment(self, idx):
        comment = wp.WordPressEditComment()
        comment.status = 'approve'
        comment.date_created_gmt = self.comments[idx]['date_created_gmt']
        comment.content = self.comments[idx]['content']
        comment.author = self.comments[idx]['author']
        comment.author_url = self.comments[idx]['author_url']
        comment.author_email = self.comments[idx]['author_email']
        comment_id = self.comments[idx]['comment_id']

        try:
            self.blog.editComment(comment_id, comment)
        except:
            note(LABELS.loc.wp_err_cant_appr_cmt,"error")
            return False

        note(LABELS.loc.wp_info_cmt_approved,"info")
        self.comments[idx]['status'] = 'approve'

        return True

    def delete_comment(self,idx):
        try:
            self.blog.deleteComment( self.comments[idx]['comment_id'] )
        except:
            note(LABELS.loc.wp_err_cant_del_cmt,"error")
            return False
        
        del self.comments[idx]
        note(LABELS.loc.wp_info_cmt_del,"info")
        
        return True
            
    def set_blog(self):
        if DB["proxy_enabled"] == u"True":
            user = unicode_to_utf8( DB["proxy_user"] )
            addr = unicode_to_utf8( DB["proxy_addr"] )
            port = unicode_to_utf8( DB["proxy_port"] )
            user = unicode_to_utf8( DB["proxy_user"] )
            pwrd = unicode_to_utf8( DB["proxy_pass"] )
            
            if user:
                proxy = "http://%s:%s@%s:%s" % (user,pwrd,addr,port)
            else:
                proxy = "http://%s:%s" % (addr,port)
                
            transp = UrllibTransport()
            transp.set_proxy(proxy)
            os.environ["http_proxy"] = proxy # for urllib
        else:
            transp = None
            os.environ["http_proxy"] = ""
            del os.environ["http_proxy"]
            
        blog_url = unicode_to_utf8( DB["blog"] ) + "/xmlrpc.php"
        self.blog = wp.WordPressClient(blog_url, unicode_to_utf8( DB["user"] ), unicode_to_utf8( DB["pass"] ), transp)
        self.blog.selectBlog(0)
        

BLOG = WordPressWrapper()

