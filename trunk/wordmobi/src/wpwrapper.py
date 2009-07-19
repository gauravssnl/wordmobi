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
from wmlocale import LABELS
from wmglobals import DEFDIR, PERSIST, VERSION
from types import IntType
import simplejson as json
import e32
if e32.in_emulator():
    import cPickle as pickle
else:
    import pickle

__all__ = [ "WordPressWrapper", "BLOG" ]

class WordPressWrapper(object):
    def __init__(self):
        self.persist_name = PERSIST
        self.posts = []
        self.comments = []
        self.categories = []
        self.tags = []
        self.cat_dict = {}
        self.cat_default = []
        self.curr_blog =  {}
        self.num_posts = 20
        self.num_comments = 30
        self.blog_key = ""
        self.blog_data = {}
        #self.load()
        self.refresh()
        self.build_cat_dict()
        self.blog = None
        self.proxy = ""
        
    def refresh(self):
        """ Update variables related to multiple idioms support
        """
        # just use default values if categories were not retrieved yet
        # but considering possible new locale
        if self.categories == self.cat_default:
            self.categories = []
        self.cat_default = [ { 'categoryName':LABELS.loc.wp_list_uncategorized,
                               'categoryId':'1',
                               'parentId':'0' } ]
        if not self.categories:
            self.categories = self.cat_default

    def category_names_list(self):
        """ Return a list with all category names. The name order must match with
            self.categories, so it is not possible to use dict keys.
        """
        return map( lambda x:  x['categoryName'] , self.categories)

    def categoryName2Id(self,cat):
        if self.cat_dict.has_key(cat):
            return (self.cat_dict[cat]['categoryId'],
                    self.cat_dict[cat]['parentId'])
        return ('0','0')
            
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

        self.build_cat_dict()
        self.save()
        return True

    def build_cat_dict(self):
        self.cat_dict = {}
        for c in self.categories:
            self.cat_dict[c['categoryName']] = c
                    
    def delete_category(self, item):
        retval = False
        cat_id = self.categories[item]['categoryId']
        cat_name = self.categories[item]['categoryName']
        
        try:
            res = self.blog.deleteCategory(cat_id)
        except:
            note(LABELS.loc.wp_err_cant_del_cat % cat_name,"error")
        else:
            if res:
                del self.categories[item]
                # categories can not be empty
                if not self.categories:
                    self.categories = self.cat_default 
                self.build_cat_dict()
                retval = True
                note(LABELS.loc.wp_info_cat_del % cat_name,"info")
            else:
                note(LABELS.loc.wp_err_cant_del_cat % cat_name,"error")
    
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

    def tag_names_list(self):
        """ Return a list with all tags names. The name order must match with
            self.tags, so it is not possible to use dict keys.
        """
        return map(lambda x:  x['name'] , self.tags)
    
    def update_tags(self):
        """ Download all tags from wordpress site and update local data.
            Return True (tags updates) or False (tags not updated)
        """
        try:
            self.tags = self.blog.getTags()
        except:
            note(LABELS.loc.tg_err_cant_updt_tags,"error")
            return False

        for i in range(len(self.tags)):
            try:
                self.tags[i]['name'] = decode_html(self.tags[i]['name'])
            except:
                self.tags[i]['name'] = utf8_to_unicode(self.tags[i]['name'])

        self.tags.sort(lambda x,y:cmp(x['name'],y['name']))
        
        return True
        
    def update_posts_cats_and_tags(self):
        """ Update local information about post titles, categories and tags.
            If all three as updated without error, return True. Otherwise,
            return False.
        """
        try:
            posts = self.blog.getRecentPostTitles(self.num_posts)
        except:
            note(LABELS.loc.wp_err_cant_updt_post,"error")
            return False

        mod_pst = []
        mod_idx = []
        new_pst = []
        for n in range(len(self.posts)):
            p = self.posts[n]
            if self.post_is_only_local(p):
                new_pst.append(p)
            elif self.post_is_remote(p) and self.post_is_local(p):
                # post edited locally: preserve it
                mod_pst.append(p['postid'])
                mod_idx.append(n)
        if mod_pst:
            for n in range(len(posts)):
                try:
                    idx = mod_pst.index(posts[n]['postid'])
                except:
                    continue
                # copy edited post
                posts[n] = self.posts[mod_idx[idx]]
        posts += new_pst
        self.posts = posts
        def _time_sort(x,y):
            if x['dateCreated'] > y['dateCreated']:
                return -1
            elif x['dateCreated'] < y['dateCreated']:
                return 1
            else:
                return 0
        self.posts.sort(_time_sort)
        del posts
        return self.update_categories() and self.update_tags()
        
    def get_post(self,item):
        try:
            self.posts[item] = self.blog.getPost( self.posts[item]['postid'] )
        except:
            note(LABELS.loc.wp_err_cant_downl_post,"error")
            return False
        self.save()
        return True

    def upload_images(self, fname):
        app.title = LABELS.loc.wp_info_upld_img % ( os.path.basename(fname) ) 
        try:
            img_src = self.blog.newMediaObject(fname)
        except:
            note(LABELS.loc.wp_err_cant_upld_img % fname,"error")
            return None
        
        return img_src
    
    def new_post(self, title, contents, categories, tags, publish, offline_idx=-1):
        """ Upload a new post, where:
        
            - title: post title, in unicode
            - contents: post contents, in unicode
            - categories: array of category names in unicode
            - tags: array of tag names in unicode
            - publish: draft post (False, not published) or final post (True, published)
            - offline_idx: post index, if it is offline,
            
            Return the new post ID (success) or -1 (error)
        """
        app.title = LABELS.loc.wp_info_upld_post_cont
                      
        soup = BeautifulSoup(unicode_to_utf8(contents))
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n"," ")
        app.title = LABELS.loc.wp_info_upld_post_cont 

        post = wp.WordPressPost()
        post.description = contents + unicode_to_utf8(LABELS.loc.promo_phrase)
                      
        post.title = unicode_to_utf8( title )
        post.categories = [ self.categoryName2Id(c)[0] for c in categories ]
        post.keywords = ",".join([ unicode_to_utf8(t) for t in tags ])
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
                # indicate that the corresponding offline post now has a remote copy
                if offline_idx >= 0:              
                    self.posts[offline_idx] = p
                else:
                    self.posts.insert( 0, p )
            except:
                note(LABELS.loc.wp_err_cant_updt_post_list,"error")
            self.save()
        return npost

    def save_new_post(self, title, contents, categories, tags, publish):
        """ Instead posting, save the post locally.
            We need to create a post like that one provided by xmlrpclib (utf8).
            Otherwise, WM will fail when decoding this post.
            Just a new dict is added (wordmobi), for controlling.
            See parameters in new_post.
        """
        if publish:
            pub = 'publish'
        else:
            pub = 'draft'
        dt = time.gmtime()
        pst = { 'title': unicode_to_utf8(title),
                'description': unicode_to_utf8(contents),
                'categories':[ unicode_to_utf8(c) for c in categories ],
                'mt_keywords':",".join([ unicode_to_utf8(t) for t in tags ]),
                'post_status':pub,
                'dateCreated':DateTime(time.mktime(dt)),
                'mt_text_more':'',
                'wordmobi':True
                }
        self.posts.insert(0,pst)
        self.save()

    def post_is_local(self,obj):
        """ Check if a post is saved locally. It may be or not a remote copy.
            Obj is a post index or the post itself.
        """
        if isinstance(obj,IntType):
            local = self.posts[obj].has_key('wordmobi')
        else:
            local = obj.has_key('wordmobi')
        return local

    def post_is_remote(self,obj):
        """ Check if a post is remote.
            Obj is a post index or the post itself.
        """
        if isinstance(obj,IntType):
            remote = self.posts[obj].has_key('postid')
        else:
            remote = obj.has_key('postid')

        return remote

    def post_is_only_remote(self,obj):
        """ Check if a post is only remote.
            Obj is a post index or the post itself.
        """
        return (self.post_is_remote(obj) and (not self.post_is_local(obj)))
        
    def post_is_only_local(self,obj):
        """ Check if the post exists only locally, no remote copy exists.
            Obj is a post index or the post itself.
        """
        return (self.post_is_local(obj) and (not self.post_is_remote(obj)))
    
    def edit_post(self, title, contents, categories, tags, post_idx, publish):
        """ Update a post. Return True or False, indicating if the updating
            operation was sucessfuly completed or not
        """
        # when local post is edited it does not have a postid, in such case we need to
        # create a new post instead updating an existing one
        if self.post_is_only_local(post_idx):
            np_id = self.new_post(title, contents, categories, tags, publish, post_idx)
            return (np_id >= 0)
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
        post.id = self.posts[post_idx]['postid']
        post.title = unicode_to_utf8( title )
        post.description = contents
        post.categories = [ self.categoryName2Id(c)[0] for c in categories ]
        post.keywords = ",".join([ unicode_to_utf8(t) for t in tags ])
        post.allowComments = True
        post.permaLink = self.posts[post_idx]['permaLink']
        post.textMore = self.posts[post_idx]['mt_text_more']
        post.excerpt = self.posts[post_idx]['mt_excerpt']
       
        try:
            npost = self.blog.editPost(post.id, post, publish)
        except:
            note(LABELS.loc.wp_err_cant_updt_the_post,"error")
            return False
        else:
            app.title = LABELS.loc.wp_info_updt_post_list
            try:
                upd_post = self.blog.getPost(post.id)
            except:
                note(LABELS.loc.wp_err_cant_updt_post_list,"error")
            else:
                self.posts[post_idx] = upd_post

        self.save()
        return True

    def save_exist_post(self, title, contents, categories, tags, post_idx, publish):
        if publish:
            pub = 'publish'
        else:
            pub = 'draft'         
        self.posts[post_idx]['title'] = unicode_to_utf8(title)
        self.posts[post_idx]['description'] = unicode_to_utf8(contents)
        self.posts[post_idx]['categories'] = [ unicode_to_utf8(c) for c in categories ]
        self.posts[post_idx]['mt_keywords'] = ",".join([ unicode_to_utf8(t) for t in tags ])
        self.posts[post_idx]['post_status'] = pub
        if not self.posts[post_idx].has_key('wordmobi'):
            self.posts[post_idx]['wordmobi'] = True
        self.save() 
    
    def delete_post(self,idx):
        """ Delete a post, local, remote or both
        """
        if self.post_is_remote(idx):
            try:
                self.blog.deletePost(self.posts[idx]['postid'])
            except:
                return False

        del self.posts[idx]
        self.save()
        return True

    def delete_only_remote_post(self,idx):
        """ Delete remote post, keeping local changes
        """
        if self.post_is_remote(idx):
            try:
                self.blog.deletePost(self.posts[idx]['postid'])
            except:
                return False
            del self.posts[idx]['postid']
            self.posts[idx]['dateCreated'] = DateTime(time.mktime(time.gmtime()))
            self.posts[idx]['wordmobi'] = True
            self.save()
            return True
        return False
            
    def delete_only_local_post(self,idx):
        """ Delete local changes, keeping remote post
        """
        if self.post_is_local(idx):
            # discarding any local changes in the post
            del self.posts[idx]['wordmobi']
            del self.posts[idx]['description'] # force posts download
            # try to download the post content
            self.get_post(idx)
            self.save()
            return True
        return False

    def offline_publish(self, idx):
        """ Publish the offline post with index idx.
        """   
        cats = []
        for c in self.posts[idx]['categories']:
            try:
                cats.append(decode_html(c))
            except:
                cats.append(utf8_to_unicode(c))

        tags = []
        if self.posts[idx]['mt_keywords']:
            # spliting an empty string will return a vector, this is not desired
            for t in self.posts[idx]['mt_keywords'].split(','):
                try:
                    tags.append(decode_html(t))
                except:
                    tags.append(utf8_to_unicode(t))
                
        title = utf8_to_unicode(BLOG.posts[idx]['title'])
        conts = utf8_to_unicode(BLOG.posts[idx]['description'])
        publish = self.posts[idx]['post_status'] == 'publish'
        
        if self.post_is_only_local(idx):
            BLOG.new_post(title,conts,cats,tags,publish,idx)
        else:
            self.edit_post(title,conts,cats,tags,idx,publish)

    def get_comment(self, post_idx, comment_status):
        """ Download comments for post with index post_idx with status comment_status.
            If post_idx is -1, download comments for all posts
        """
        if post_idx == -1:
            post_id = ''
        else:
            post_id = self.posts[post_idx]['postid']
        comm_info = wp.WordPressComment()
        comm_info.post_id = post_id
        comm_info.status = comment_status
        comm_info.number = self.num_comments
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
        comment.date_created_gmt = DateTime(time.mktime(time.gmtime())) # gmt time required
    
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

    def get_proxy(self):
        return self.proxy

    def check_persistence(self,blogs):
        """ Remove all data not related to any blog and keep one data
            data related do configured blogs
        """
        if os.path.exists(self.persist_name):
            f = open(self.persist_name,"rb")
            version = pickle.load(f)
            self.blog_data = pickle.load(f)
            f.close()
            if isinstance(self.blog_data,dict):
                saved_keys = self.blog_data.keys()
                new_keys = [ self.blog_hash(b["blog"],b["user"],b["pass"]) for b in blogs ] 
                for k in saved_keys:
                    if k not in new_keys:
                        del self.blog_data[k]
                f = open(self.persist_name,"wb")
                pickle.dump(VERSION,f)
                pickle.dump(self.blog_data,f)
                f.close()
                    
    def save(self):
        self.blog_data[self.blog_key] = {'categories':self.categories,
                                         'posts':self.posts,
                                         'comments':self.comments,
                                         'tags':self.tags}
        f = open(self.persist_name,"wb")
        pickle.dump(VERSION,f)
        pickle.dump(self.blog_data,f)
        f.close()

    def load(self):
        if os.path.exists(self.persist_name):
            f = open(self.persist_name,"rb")
            version = pickle.load(f)
            self.blog_data = pickle.load(f)
            f.close()
            if not isinstance(self.blog_data,dict):
                self.blog_data = {}
            self.categories = []
            self.posts = []
            self.comments = []
            self.tags = []
            if self.blog_data.has_key(self.blog_key):
                for k in ['categories', 'posts', 'comments', 'tags']:
                    if hasattr(self,k):
                        self.__setattr__(k,self.blog_data[self.blog_key][k])
            # avoid empty categories and create a valid dict
            self.refresh()
            self.build_cat_dict()                        

    def blog_hash(self,url,usr,pwd):
        """ Create a hash for each blog in use
        """
        try:
            # md5 is deprecated but it is the only available in 1.4.5
            import hashlisb as md5
        except:
            import md5

        h = md5.md5(url+usr+pwd)
        return h.hexdigest()
    
    def set_blog(self,bidx):
        self.curr_blog =  json.loads(DB["blog_list"])[bidx]
        self.num_posts = self.curr_blog["num_posts"]
        self.num_comments = self.curr_blog["num_comments"]
        if DB["proxy_enabled"] == u"True":
            user = unicode_to_utf8( DB["proxy_user"] )
            addr = unicode_to_utf8( DB["proxy_addr"] )
            port = unicode_to_utf8( DB["proxy_port"] )
            user = unicode_to_utf8( DB["proxy_user"] )
            pwrd = unicode_to_utf8( DB["proxy_pass"] )
            
            if user:
                self.proxy = "http://%s:%s@%s:%s" % (user,pwrd,addr,port)
            else:
                self.proxy = "http://%s:%s" % (addr,port)
                
            transp = UrllibTransport()
            transp.set_proxy(self.proxy)
            os.environ["http_proxy"] = self.proxy # for urllib
        else:
            transp = None
            self.proxy = ""
            os.environ["http_proxy"] = ""
            del os.environ["http_proxy"]

        if self.curr_blog["blog"].endswith(u".php"):
            # advance mode: user has different url for xmlrpc, do not change it
            blog_url = unicode_to_utf8(self.curr_blog["blog"])
        else:
            # standard mode: use type an blog address only
            blog_url = unicode_to_utf8(self.curr_blog["blog"]) + "/xmlrpc.php"
        
        self.blog = wp.WordPressClient(blog_url,
                                       unicode_to_utf8(self.curr_blog["user"]),
                                       unicode_to_utf8(self.curr_blog["pass"]),
                                       transp)
        self.blog.selectBlog(0)
        self.blog_key = self.blog_hash(self.curr_blog["blog"],
                                       self.curr_blog["user"],
                                       self.curr_blog["pass"])
        self.load()
        

BLOG = WordPressWrapper()

