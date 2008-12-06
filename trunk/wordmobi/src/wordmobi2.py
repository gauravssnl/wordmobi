# -*- coding: utf-8 -*-
import e32, e32dbm, key_codes
import datetime, os
from appuifw import *
import wordpresslib as wp
from posts import NewPost, EditPost
from settings import *
from wmutil import *
from comments import EditComment, NewComment
from wmproxy import UrllibTransport
from socket import select_access_point, access_point, access_points, set_default_access_point
from beautifulsoup import BeautifulSoup
from xmlrpclib import DateTime

__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = "0.2.10"
__copyright__ = "Copyright (c) 2008- Marcelo Barros de Almeida"
__license__ = "GPLv3"

PROMO_PHRASE = "<br><br>Posted by <a href=\"http://wordmobi.googlecode.com\">Wordmobi</a>"
DEFDIR = "e:\\wordmobi\\"

class Persist(dict):
    __highlander = None
    DBNAME = os.path.join(DEFDIR,"wordmobi")
    DEFVALS = {"user":u"username",
               "pass":u"password",
               "blog":u"http://blogname.wordpress.com",
               "email":u"@",
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

class BaseTabWin(object):
    
    ui_lock = False
    tabs = { "TABS":[], "LABELS":[] }
    last_tab = 0
    
    def __init__(self, title, body, exit_key_handler=lambda:None):
        #self.ui_lock = False
        self.app_title = title
        self.last_idx = 0        
        self.menu = [(u"Exit", self.close_app)]
        self.body = body
        self.exit_key_handler = exit_key_handler

        self.refresh()

    def set_title(self,title):
        app.title = self.app_title = title
        
    def register_tabs(tabs, labels):
        BaseTabWin.tabs = { "TABS": tabs, "LABELS":labels }
        app.set_tabs( BaseTabWin.tabs['LABELS'], BaseTabWin.tab_handler )
        BaseTabWin.tab_handler( 0 ) 
        
    register_tabs = staticmethod( register_tabs )

    def tab_handler(idx):
        BaseTabWin.last_tab = idx
        BaseTabWin.tabs['TABS'][idx].refresh()
        app.activate_tab( idx )        

    tab_handler = staticmethod( tab_handler )
        
    def refresh(self):
        if not self.ui_is_locked():
            app.title = self.app_title
            app.menu = self.menu
            app.body = self.body
            app.exit_key_handler = self.close_app

    def disable_tabs():
        app.set_tabs( [], lambda: None )

    disable_tabs = staticmethod( disable_tabs )

    def restore_tabs():
        app.set_tabs( BaseTabWin.tabs['LABELS'], BaseTabWin.tab_handler )
        app.activate_tab( BaseTabWin.last_tab )
        
    restore_tabs = staticmethod( restore_tabs )

    def lock_ui(self,msg = u""):
        BaseTabWin.ui_lock = True
        app.menu = []
        BaseTabWin.disable_tabs()
        if msg:
            app.title = msg

    def unlock_ui(self):
        BaseTabWin.ui_lock = False
        app.menu = self.menu
        app.title = self.app_title
        BaseTabWin.restore_tabs()

    def ui_is_locked(self):
        return BaseTabWin.ui_lock
    
    def close_app(self):
        self.exit_key_handler()

class PostTab(BaseTabWin):
    def __init__(self, common_menu, exit_key_handler=lambda:None):

        self.headlines = []
        self.body = Listbox( [ (u"",u"") ], self.popup_check_lock )
        BaseTabWin.__init__(self, u"[1/1] Posts", self.body, exit_key_handler)
        self.body.bind(key_codes.EKeyUpArrow, self.key_up)
        self.body.bind(key_codes.EKeyDownArrow, self.key_down)
        self.menu = [( u"Posts", (
                            ( u"Update", self.update ), 
                            ( u"View/Edit", self.contents ),
                            ( u"Delete", self.delete ),
                            ( u"Comments", self.comments ),
                            ( u"New", self.new )
                            ))] + common_menu
        
    def popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.last_idx = self.body.current()
            self.popup()
            
    def popup(self):
        idx = popup_menu( [ u"Update", u"View/Edit", u"Comments", u"Delete", u"New"], u"Posts:")
        if idx is not None:
            [ self.update, self.contents, self.comments, self.delete, self.new ][idx]()

    def comments(self):
        idx = self.body.current()
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return
        #arghhh - ugly ! RTI: remote tab invocation ...
        BaseTabWin.tab_handler(1)
        BaseTabWin.tabs['TABS'][1].update_comment( idx )

    def key_up(self):
        if self.ui_is_locked() == False:
            p = self.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Posts" % (p+1,m) )

    def key_down(self):
        if self.ui_is_locked() == False:
            p = self.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Posts" % (p+1,m) )
        
    def update(self):
        self.lock_ui(u"Downloading posts..." )
        try:
            WordMobi.posts = WordMobi.blog.getRecentPostTitles( int(WordMobi.db["num_posts"]) )
        except:
            note(u"Impossible to retrieve post titles.","error")
            self.unlock_ui()
            return

        self.headlines = []
        if len(WordMobi.posts) > 0:
            for p in WordMobi.posts:
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                line1 = u"%d/%s/%d  %02d:%02d:%02d" % (d,MONTHS[mo-1],y,h,m,s)
                line2 = utf8_to_unicode( p['title'] )
                self.headlines.append( ( line1 , line2 ) )
        else:
            note( u"No posts available.", "info" )

        self.lock_ui(u"Downloading categories...")
        try:
            cats = WordMobi.blog.getCategoryList()
        except:
            note(u"Impossible to retrieve the categories list.","error")
            self.unlock_ui()
            return

        WordMobi.categories = [ decode_html(c.name) for c in cats ]
        self.unlock_ui()
        self.refresh()
    
    def upload_images(self, fname):
        self.lock_ui( u"Uploading %s..." % ( os.path.basename(fname) ) )
        try:
            img_src = WordMobi.blog.newMediaObject(fname)
        except:
            note(u"Impossible to upload %s. Try again." % fname,"error")
            return None
        
        return img_src

    def upload_new_post(self, title, contents, categories, publish):
        """ Uplaod a new or edited post. For new post, use post_id as None
        """
        self.lock_ui( u"Uploading post contents...")
                      
        soup = BeautifulSoup( unicode_to_utf8(contents) )
        for img in soup.findAll('img'):
            if os.path.isfile( img['src'] ): # just upload local files
                url = self.upload_images( img['src'] )
                if url is not None:
                    img['src'] = url

        contents = soup.prettify().replace("\n","")
        self.lock_ui( u"Uploading post contents..." )

        post = wp.WordPressPost()
        post.description = contents + PROMO_PHRASE
                      
        post.title = unicode_to_utf8( title )
        post.categories = [ WordMobi.blog.getCategoryIdFromName( unicode_to_utf8(c) ) for c in categories ]
        post.allowComments = True

        try:
            npost = WordMobi.blog.newPost(post, publish)
        except:
            note(u"Impossible to publish the post. Try again.","error")
            raise

        return npost


    def new_cbk( self, params ):
        if params is not None:
            (title,contents,categories,publish) = params

            try:
                self.upload_new_post(title, contents, categories, publish)
            except:
                return False                    

            self.lock_ui( u"Updating post list..." )
            try:
                p = WordMobi.blog.getLastPostTitle( )                
            except:
                note(u"Impossible to update post title. Try again.","error")
                self.unlock_ui()
                BaseTabWin.restore_tabs()
                self.refresh()
                return True
            
            if self.headlines[0][0] == u"<empty>":
                self.headlines = []
                WordMobi.posts = []
  
            (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
            timestamp = u"%d/%s/%d  %02d:%02d:%02d" % (d,MONTHS[mo-1],y,h,m,s) 
            self.headlines.insert( 0, ( timestamp , utf8_to_unicode( p['title'] ) ) )
            WordMobi.posts.insert( 0, p )
            
        self.unlock_ui()
        BaseTabWin.restore_tabs()
        self.refresh()
        return True

    def new(self):
        BaseTabWin.disable_tabs()
        self.dlg = NewPost( self.new_cbk, u"", u"", WordMobi.categories, [], True )
        self.dlg.run()

    def delete(self):
        idx = self.body.current()
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return

        ny = popup_menu( [u"No", u"Yes"], u"Delete post ?" )
        if ny is not None:
            if ny == 1:
                self.lock_ui(u"Deleting post...")
                try:
                    WordMobi.blog.deletePost( WordMobi.posts[idx]['postid'] )
                except:
                    self.unlock_ui()
                    note(u"Impossible to delete the post.","error")
                    return
                del self.headlines[idx]
                del WordMobi.posts[idx]
                note(u"Post deleted.","info")
                self.unlock_ui() 
                self.refresh()

    def contents_cbk(self,params):
        if params is not None:
            (title,contents,categories,post_orig, publish) = params

            self.lock_ui( u"Uploading post contents...")

            soup = BeautifulSoup( unicode_to_utf8(contents) )
            for img in soup.findAll('img'):
                if os.path.isfile( img['src'] ): # just upload local files
                    url = self.upload_images( img['src'] )
                    if url is not None:
                        img['src'] = url

            contents = soup.prettify().replace("\n","")

            post = wp.WordPressPost()
            post.id = post_orig['postid']
            post.title = unicode_to_utf8( title )
            post.description = contents
            post.categories = [ WordMobi.blog.getCategoryIdFromName( unicode_to_utf8(c) ) for c in categories ]
            post.allowComments = True
            post.permaLink = post_orig['permaLink']
            post.textMore = post_orig['mt_text_more']
            post.excerpt = post_orig['mt_excerpt']

            try:
                npost = WordMobi.blog.editPost( post.id, post, publish)
            except:
                note(u"Impossible to update the post. Try again.","error")
                self.unlock_ui()
                return False

            try:
                upd_post = WordMobi.blog.getPost(post.id)
            except:
                note(u"Impossible to update post title. Try again.","error")

            # update the list !
            for idx in range(len(WordMobi.posts)):
                if WordMobi.posts[idx]['postid'] == post.id:
                    ( line1 , line2 ) = self.headlines[idx]
                    line2 = utf8_to_unicode( post.title )
                    self.headlines[idx] = ( line1 , line2 )
                    del WordMobi.posts[idx]['description'] # force reload
                    break
    
        self.unlock_ui()
        BaseTabWin.restore_tabs()
        self.refresh()
        return True
        
    def contents(self):
        idx = self.body.current()
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return
        
        # if post was not totally retrieved yet, fetch all data
        if WordMobi.posts[idx].has_key('description') == False:
            self.lock_ui(u"Downloading post...")
            try:
                WordMobi.posts[idx] = WordMobi.blog.getPost( WordMobi.posts[idx]['postid'] )
            except:
                self.unlock_ui()
                note(u"Impossible to download the post. Try again.","error")
                return
            self.unlock_ui() 
        if WordMobi.posts[idx]['post_status'] == 'publish': # 'publish' or 'draft'
            publish = True
        else:
            publish = False

        BaseTabWin.disable_tabs()
        self.dlg = EditPost( self.contents_cbk, WordMobi.categories, WordMobi.posts[idx], publish )
        self.dlg.run()

    def refresh(self):
        BaseTabWin.refresh(self)
        if len( self.headlines ) == 0:
            self.headlines = [ (u"<empty>", u"Please, update the post list") ]
            WordMobi.posts = []
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        self.body.set_list( self.headlines, self.last_idx )
        
class CommentTab(BaseTabWin):
    def __init__(self, common_menu, exit_key_handler=lambda:None):

        self.headlines = []
        self.body = Listbox( [ (u"",u"") ], self.popup_check_lock )
        BaseTabWin.__init__(self,u"[1/1] Comments", self.body, exit_key_handler)
        self.body.bind(key_codes.EKeyUpArrow, self.key_up)
        self.body.bind(key_codes.EKeyDownArrow, self.key_down)
        self.menu = [( u"Comments", (
                            ( u"Update", self.update ), 
                            ( u"View/Edit", self.contents ),
                            ( u"Delete", self.delete ),
                            ( u"New/Reply", self.new )
                            ))] + common_menu
        
    def popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.last_idx = self.body.current()
            self.popup()
            
    def popup(self):
        menu = [ u"Update", u"View/Edit", u"Delete", u"New/Reply"]
        cbk = [ self.update, self.contents, self.delete, self.new ]
        if self.headlines[0][0] != u"<empty>":
            if WordMobi.comments[self.body.current()]['status'] != 'approve':
                menu.append( u"Approve" )
                cbk.append( self.moderate )
        idx = popup_menu( menu, u"Comments:")
        if idx is not None:
            cbk[idx]()

    def key_up(self):
        if self.ui_is_locked() == False:
            p = self.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Comments" % (p+1,m) )

    def key_down(self):
        if self.ui_is_locked() == False:
            p = self.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Comments" % (p+1,m) )

    def translate_status(self,status):
        if status == 'approve':
            translated = 'Published'
        elif status == 'spam':
            translated = '!!Spam!!'
        else:
            translated = 'Moderate'

        return translated
        
    def moderate(self):
        idx = self.body.current()
        self.lock_ui(u"Approving comment %s" % utf8_to_unicode( WordMobi.comments[idx]['content'][:15] ))
        comment = wp.WordPressEditComment()
        comment.status = 'approve'
        comment.date_created_gmt = WordMobi.comments[idx]['date_created_gmt']
        comment.content = WordMobi.comments[idx]['content']
        comment.author = WordMobi.comments[idx]['author']
        comment.author_url = WordMobi.comments[idx]['author_url']
        comment.author_email = WordMobi.comments[idx]['author_email']
        comment_id = WordMobi.comments[idx]['comment_id']

        try:
            WordMobi.blog.editComment(comment_id, comment)
        except:
            note(u"Impossible to approve the comment. Try again.","error")
            self.unlock_ui()
            return

        note(u"Comment approved.","info")

        try:
            c = WordMobi.blog.getComment( comment_id )
        except:
            note(u"Impossible to update the comment list. Try again.","error")
            WordMobi.comments[idx]['status'] = 'approve'
            c = None

        if c:
            (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
            line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']), c['author'])
            line2 = utf8_to_unicode( c['content'] )
            WordMobi.comments[idx] = c
            self.headlines[idx] = ( line1 , line2 )
        
        self.unlock_ui()
        self.refresh()
        
    def update(self):
        res = popup_menu( [ u"Specific post", u"All posts", ], u"Comments for ?")
        if res is None:
            return
        if res == 0:
            if len(WordMobi.posts) == 0:
                note(u"Please, first update the post list.","info")
                return
            self.set_title( u"Which post?" )
            post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in WordMobi.posts ], search_field=1)
            if post_idx is None:
                return
        else:
            post_idx = -1

        self.update_comment(post_idx)
        
    def update_comment(self,post_idx):
        if post_idx == -1:
            note(u"Not implemented.","info")
        else:
            self.lock_ui(u"Downloading comments...")
            post_id = WordMobi.posts[post_idx]['postid']
            comm_info = wp.WordPressComment()
            comm_info.post_id = post_id
            comm_info.number = WordMobi.db['num_comments']
            try:
                comments = WordMobi.blog.getComments( comm_info )
            except:
                note(u"Impossible to download comments. Try again.","error")
                self.unlock_ui()                
                self.refresh()
                return

            if len( comments ) == 0:
                note(u"No comments for this post.","info")
            else:
                self.headlines = []
                for c in comments:
                    (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                    line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']),utf8_to_unicode( c['author'] ))
                    line2 = utf8_to_unicode( c['content'] )
                    WordMobi.comments.append( c )
                    self.headlines.append( ( line1 , line2 ) )
                                    
        self.unlock_ui()
        self.refresh()

    def new_cbk(self, params):
        if params is not None:

            (post_id, email, realname, website, contents) = params
            
            self.lock_ui( u"Sending comment %s" % contents[:15] )
            
            comment = wp.WordPressNewComment()
            comment.status = 'approve'
            comment.content = unicode_to_utf8( contents )
            comment.author = unicode_to_utf8( realname )
            comment.author_url = unicode_to_utf8( website )
            comment.author_email = unicode_to_utf8( email )

            try:
                comment_id = WordMobi.blog.newComment( post_id, comment )
            except:
                note(u"Impossible to send the comment. Try again.","error")
                self.unlock_ui()
                return False
            
            try:
                c = WordMobi.blog.getComment( comment_id )
            except:
                note(u"Impossible to update the comment list. Try again.","error")
                c = None

            if c:
                (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']), c['author'])
                line2 = utf8_to_unicode( c['content'] )
                if self.headlines[0][0] == u"<empty>":
                    WordMobi.comments = [ c ]
                    self.headlines= [ ( line1 , line2 ) ]
                else:
                    WordMobi.comments.insert( 0, c )
                    self.headlines.insert( 0, ( line1 , line2 ) )
                
            self.unlock_ui()

        BaseTabWin.restore_tabs()
        self.refresh()
        return True
    
    def new(self):
        if self.headlines[0][0] == u"<empty>":
            if len(WordMobi.posts) == 0:
                note(u"Please, first update the post list.","info")
                return
            self.set_title( u"Which post?" )
            idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in WordMobi.posts ], search_field=1)
            # idx may be -1 if list is empty and user press OK... strange ... why not None ?
            if idx is None:
                return
            post_id = WordMobi.posts[idx]['postid']
        else:
            idx = self.body.current()
            post_id = WordMobi.comments[idx]['post_id']

        BaseTabWin.disable_tabs()
               
        self.dlg = NewComment( self.new_cbk, post_id, WordMobi.db['realname'],
                               WordMobi.db['email'],WordMobi.db['blog'], u"")
        self.dlg.run()
        

    def delete(self):
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the comment list.", "info" )
            return
        
        ny = popup_menu( [u"No", u"Yes"], u"Delete comment ?")
        if ny == 1:
            idx = self.body.current()
            self.lock_ui(u"Deleting comment %s" % utf8_to_unicode( WordMobi.comments[idx]['content'][:15] ))

            try:
                WordMobi.blog.deleteComment( WordMobi.comments[idx]['comment_id'] )
            except:
                note(u"Impossible to delete the comment. Try again.","error")
                self.unlock_ui()
                return

            del WordMobi.comments[idx]
            del self.headlines[idx]
            
            note(u"Comment deleted.","info")
            self.unlock_ui()
            self.refresh()

    def contents_cbk(self,params):
        if params is not None:

            (idx, email, realname, website, contents) = params
            
            self.lock_ui( u"Sending comment %s" % contents[:15] )

            comment_id = WordMobi.comments[idx]['comment_id']
            comment = wp.WordPressEditComment()
            comment.status = 'approve'
            comment.content = unicode_to_utf8( contents )
            comment.author = unicode_to_utf8( realname )
            comment.author_url = unicode_to_utf8( website )
            comment.author_email = unicode_to_utf8( email )
            comment.date_created_gmt = DateTime( time.mktime(time.gmtime()) ) # gmt time required
        
            try:
                WordMobi.blog.editComment(comment_id, comment)
            except:
                note(u"Impossible to update the comment. Try again.","error")
                self.unlock_ui()
                return False

            try:
                c = WordMobi.blog.getComment( comment_id )
            except:
                note(u"Impossible to update the comment list. Try again.","error")
                c = None

            if c:
                (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']), c['author'])
                line2 = utf8_to_unicode( c['content'] )
                WordMobi.comments[idx] = c
                self.headlines[idx] = ( line1 , line2 ) 
                
            self.unlock_ui()

        BaseTabWin.restore_tabs()
        self.refresh()
        return True
    
    def contents(self):
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the comment list.", "info" )
            return
        
        BaseTabWin.disable_tabs()
        idx = self.body.current()
        self.dlg = EditComment( self.contents_cbk, idx, \
                                utf8_to_unicode( WordMobi.comments[idx]['author'] ), \
                                utf8_to_unicode( WordMobi.comments[idx]['author_email'] ), \
                                utf8_to_unicode( WordMobi.comments[idx]['author_url'] ), \
                                utf8_to_unicode( WordMobi.comments[idx]['content'] ))
        self.dlg.run()
    
    def refresh(self):
        BaseTabWin.refresh(self)
        if len( self.headlines ) == 0:
            self.headlines = [ (u"<empty>", u"Please, update the comment list") ]
            WordMobi.comments = []
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        self.body.set_list( self.headlines, self.last_idx )

class CategoryTab(BaseTabWin):
    def __init__(self, common_menu, exit_key_handler=lambda:None):
        self.body = Listbox( [ (u"") ], self.update_value_check_lock )
        BaseTabWin.__init__(self,u"Categories", self.body, exit_key_handler)
        self.menu = [( u"Categories", (
                            ( u"Update", self.update ), 
                            ( u"Delete", self.delete ),
                            ( u"New", self.new )
                            ))] + common_menu
    def update_value_check_lock(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def new(self):
        pass

    def refresh(self):
        BaseTabWin.refresh(self)
        lst_values = [ (u"E"), (u"F") ]        
        self.body.set_list(lst_values, self.last_idx)
        
        
class WordMobi(object):
    db = None
    proxy = None
    blog = None
    posts = []
    comments = []
    categories = []
    
    def __init__(self):
        
        self.lock = e32.Ao_lock()
        self.app_title = u"Wordmobi"
        self.last_tab = 0
        self.def_ap = {}
        
        self.check_dirs()
        WordMobi.db = Persist()
        WordMobi.db.load()
        
        self.menu = [ ( u"Settings", (
                            ( u"Blog", self.config_wordmobi ),
                            ( u"Proxy",self.config_network ),
                            ( u"Access Point", self.sel_access_point )
                            )),
                        ( u"About", self.about_wordmobi ),
                        ( u"Exit", self.close_app )]


        tabs = [ PostTab(self.menu, self.close_app), CommentTab(self.menu, self.close_app), CategoryTab(self.menu, self.close_app) ]
        labels = [ u"Posts", u"Comments", u"Categories" ]
        BaseTabWin.register_tabs(  tabs, labels )        
        
        self.sel_access_point()        
        self.refresh()

    def check_dirs(self):
        if not os.path.exists(DEFDIR):
            try:
                os.makedirs(DEFDIR)
                os.makedirs(os.path.join(DEFDIR,"cache"))
                os.makedirs(os.path.join(DEFDIR,"images"))
            except:
                note(u"Could't create wordmobi directory %s" % DEFDIR,"error")

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
        if WordMobi.db["proxy_enabled"] == u"True":
            user = unicode_to_utf8( WordMobi.db["proxy_user"] )
            addr = unicode_to_utf8( WordMobi.db["proxy_addr"] )
            port = unicode_to_utf8( WordMobi.db["proxy_port"] )
            user = unicode_to_utf8( WordMobi.db["proxy_user"] )
            pwrd = unicode_to_utf8( WordMobi.db["proxy_pass"] )
            
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
            
        blog = unicode_to_utf8( WordMobi.db["blog"] ) + "/xmlrpc.php"
        WordMobi.blog = wp.WordPressClient(blog, unicode_to_utf8( WordMobi.db["user"] ), unicode_to_utf8( WordMobi.db["pass"] ), transp)
        WordMobi.blog.selectBlog(0)
        
    def refresh(self):
        app.exit_key_handler = self.close_app
        
    def close_app(self):
        self.lock.signal()

    def config_wordmobi_cbk(self,params):
        if params is not None:
            ( WordMobi.db["blog"], WordMobi.db["user"],
              WordMobi.db["pass"], WordMobi.db["email"],
              WordMobi.db["realname"], np, nc ) = params
            
            WordMobi.db["num_posts"] = utf8_to_unicode( str(np) )
            WordMobi.db["num_comments"] = utf8_to_unicode( str(nc) )
            
            WordMobi.db.save()
            self.set_blog_url()
            
        self.refresh()
        return True
            
    def config_wordmobi(self):
        self.dlg = BlogSettings( self.config_wordmobi_cbk,\
                                 WordMobi.db["blog"], \
                                 WordMobi.db["user"], \
                                 WordMobi.db["pass"], \
                                 WordMobi.db["email"], \
                                 WordMobi.db["realname"], \
                                 int(WordMobi.db["num_posts"]), \
                                 int(WordMobi.db["num_comments"]) )
        self.dlg.run()
        
    def config_network_cbk(self,params):
        if params is not None:
            ( WordMobi.db["proxy_enabled"], WordMobi.db["proxy_addr"], port,
              WordMobi.db["proxy_user"], WordMobi.db["proxy_pass"] ) = params
            WordMobi.db["proxy_port"] = utf8_to_unicode( str(port) )
            WordMobi.db.save()
            self.set_blog_url()
        self.refresh()
        return True
    
    def config_network(self):
        self.dlg = ProxySettings( self.config_network_cbk,\
                                  WordMobi.db["proxy_enabled"], \
                                  WordMobi.db["proxy_addr"], \
                                  int(WordMobi.db["proxy_port"]), \
                                  WordMobi.db["proxy_user"], \
                                  WordMobi.db["proxy_pass"])
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
            
    def run(self):
        old_title = app.title
        self.refresh()
        self.lock.wait()
        self.clear_cache()
        app.set_tabs( [], None )
        app.title = old_title
        app.menu = []
        app.body = None
        ### app.set_exit()

if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
