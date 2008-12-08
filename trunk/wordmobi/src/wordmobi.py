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
import urllib, time


__author__ = "Marcelo Barros de Almeida (marcelobarrosalmeida@gmail.com)"
__version__ = "0.3.3"
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

    def get_title(self):
        return app.title
        
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
                            ( u"List  Comments", self.comments ),
                            ( u"Create new", self.new )
                            ))] + common_menu
        
    def popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.last_idx = self.body.current()
            self.popup()
            
    def popup(self):
        idx = popup_menu( [ u"Update", u"View/Edit", u"List Comments", u"Delete", u"Create new"], u"Posts:")
        if idx is not None:
            [ self.update, self.contents, self.comments, self.delete, self.new ][idx]()

    def comments(self):
        idx = self.body.current()
        if self.headlines[0][0] == u"<empty>":
            note( u"Please, update the post list.", "info" )
            return
        BaseTabWin.tab_handler(1)
        if not BaseTabWin.tabs['TABS'][1].update_comment( idx ):
            self.refresh()

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
            return False

        self.headlines = []
        if len(WordMobi.posts) > 0:
            for p in WordMobi.posts:
                (y, mo, d, h, m, s) = parse_iso8601( p['dateCreated'].value )
                line1 = u"%d/%s/%d  %02d:%02d:%02d" % (d,MONTHS[mo-1],y,h,m,s)
                line2 = utf8_to_unicode( p['title'] )
                self.headlines.append( ( line1 , line2 ) )
        else:
            note( u"No posts available.", "info" )

        self.unlock_ui()
        BaseTabWin.tabs['TABS'][2].update()

        self.set_title(u"Posts")
        self.refresh()
        return True
    
    def upload_images(self, fname):
        self.lock_ui( u"Uploading %s..." % ( os.path.basename(fname) ) )
        try:
            img_src = WordMobi.blog.newMediaObject(fname)
        except:
            note(u"Impossible to upload %s. Try again." % fname,"error")
            return None
        
        return img_src

    def categoryName2Id(self,cat):
        for c in WordMobi.categories:
            if c['categoryName'] == cat:
                return (c['categoryId'], c['parentId'])

    def categoryNamesList(self):
        return map( lambda x: decode_html( x['categoryName'] ), WordMobi.categories)
            
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
        post.categories = [ self.categoryName2Id( unicode_to_utf8(c) )[0] for c in categories ]
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
        self.dlg = NewPost( self.new_cbk, u"", u"", self.categoryNamesList(), [], True )
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
            post.categories = [ self.categoryName2Id( unicode_to_utf8(c) )[0] for c in categories ]
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
        self.dlg = EditPost( self.contents_cbk, self.categoryNamesList(), WordMobi.posts[idx], publish )
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
                            ( u"Create new/Reply", self.new )
                            ))] + common_menu
        
    def popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.last_idx = self.body.current()
            self.popup()
            
    def popup(self):
        menu = [ u"Update", u"View/Edit", u"Delete", u"Create new/Reply"]
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
            translated = 'Moderated'
        elif status == 'spam':
            translated = '!!Spam!!'
        else:
            translated = 'Unmoderated'

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
        res = popup_menu( [ u"One post", u"All posts", ], u"Comments for ?")
        
        if res is None:
            return False

        if len(WordMobi.posts) == 0:
            if not BaseTabWin.tabs['TABS'][0].update():
                note(u"Impossible to update the post list.","info")
                self.refresh()
                return False
        
        if res == 0:
            t = self.get_title()
            self.set_title( u"Which post?" )
            post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in WordMobi.posts ], search_field=1)
            self.set_title( t )
            if post_idx is None:
                self.refresh()
                return False
        else:
            post_idx = -1

        self.update_comment(post_idx)
        self.set_title(u"Comments")
        self.refresh()
        return True
        
    def update_comment(self,post_idx):
        stat_lst = [ u"Any", u"Spam", u"Moderated", u"Unmoderated" ]
        item = popup_menu( stat_lst, u"With post status:")
        if item is None:
            return False
        status =  ( "", "spam", "approve", "hold" )[item]
        
        if post_idx == -1:
            all_comments = []
            np = len(WordMobi.posts)
            for n in range(len(WordMobi.posts)):
                self.lock_ui(u"[%d/%d] Downloading comments ..." % (n+1,np))
                post_id = WordMobi.posts[n]['postid']
                comm_info = wp.WordPressComment()
                comm_info.post_id = post_id
                comm_info.status = status
                comm_info.number = WordMobi.db['num_comments']

                try:
                    comments = WordMobi.blog.getComments( comm_info )
                except:
                    self.lock_ui(u"[%d/%d] Failed !" % (n+1,np))
                    e32.ao_sleep(0.5)
                    continue
                
                all_comments = all_comments + comments

            if len( all_comments ) == 0:
                note(u"No comments with status %s." % stat_lst[item],"info")
                self.unlock_ui()
                self.refresh()
                return False                
            else:
                self.headlines = []
                WordMobi.comments = []
                for c in all_comments:
                    (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                    line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']),utf8_to_unicode( c['author'] ))
                    line2 = utf8_to_unicode( c['content'] )
                    WordMobi.comments.append( c )
                    self.headlines.append( ( line1 , line2 ) )
        else:
            self.lock_ui(u"Downloading comments ...")
            post_id = WordMobi.posts[post_idx]['postid']
            comm_info = wp.WordPressComment()
            comm_info.post_id = post_id
            comm_info.status = status
            comm_info.number = WordMobi.db['num_comments']
            try:
                comments = WordMobi.blog.getComments( comm_info )
            except:
                note(u"Impossible to download comments. Try again.","error")
                self.unlock_ui()                
                self.refresh()
                return False

            if len( comments ) == 0:
                note(u"No comments with status %s." % stat_lst[item],"info")
                self.unlock_ui()
                self.refresh()
                return False
            else:
                self.headlines = []
                WordMobi.comments = []
                for c in comments:
                    (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                    line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']),utf8_to_unicode( c['author'] ))
                    line2 = utf8_to_unicode( c['content'] )
                    WordMobi.comments.append( c )
                    self.headlines.append( ( line1 , line2 ) )
                                    
        self.unlock_ui()
        self.refresh()
        return True

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
        self.headlines = []        
        self.body = Listbox( [ (u"") ], self.popup_check_lock )
        BaseTabWin.__init__(self,u"[1/1] Categories", self.body, exit_key_handler)
        self.body.bind(key_codes.EKeyUpArrow, self.key_up)
        self.body.bind(key_codes.EKeyDownArrow, self.key_down)        
        self.menu = [( u"Categories", (
                            ( u"Update", self.update ), 
                            ( u"Delete", self.delete ),
                            ( u"Create new", self.new )
                            ))] + common_menu

    def popup_check_lock(self):
        if self.ui_is_locked() == False:
            self.last_idx = self.body.current()
            self.popup()
            
    def popup(self):
        idx = popup_menu( [ u"Update", u"Delete", u"Create new"], u"Catebories:")
        if idx is not None:
            [ self.update, self.delete, self.new ][idx]()

    def key_up(self):
        if self.ui_is_locked() == False:
            p = self.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Categories" % (p+1,m) )

    def key_down(self):
        if self.ui_is_locked() == False:
            p = self.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Categories" % (p+1,m) )


    def update(self):
        self.lock_ui(u"Downloading categories...")
        try:
            WordMobi.categories = WordMobi.blog.getCategories()
        except:
            note(u"Impossible to retrieve the categories list.","error")
            self.unlock_ui()
            self.refresh()
            return

        self.headlines = []
        for c in WordMobi.categories:
            c['categoryName'] = decode_html(c['categoryName'])
            self.headlines.append( c['categoryName'] )

        self.unlock_ui()
        self.set_title(u"Categories")
        self.refresh()

    def delete(self):
        if self.headlines[0] == u"<empty>":
            note( u"Please, update the category list.", "info" )
            return
        
        item = self.body.current()
        cat_name = self.headlines[item]
        ny = popup_menu( [u"No", u"Yes"], u"Delete %s ?" % cat_name)
        if ny is not None:
            if ny == 1:
                cat_id = WordMobi.categories[item]['categoryId']
                self.lock_ui(u"Deleting category %s ..." % cat_name)
                try:
                    res = WordMobi.blog.deleteCategory(cat_id)
                except:
                    note(u"Impossible to delete category %s." % cat_name,"error")
                    
                if res == True:
                    del self.headlines[item]
                    del WordMobi.categories[item]
                    note(u"Category %s deleted." % cat_name,"info")
                else:
                    note(u"Impossible to delete category %s." % cat_name,"error")
                    
                self.unlock_ui()
            
        self.refresh()
            
    def new(self):
        cat_name = query(u"Category name:", "text", u"" )
        if cat_name is not None:
            wpc = wp.WordPressNewCategory()
            wpc.name = unicode_to_utf8( cat_name )
            wpc.slug=''
            wpc.parent_id = 0
            wpc.description = unicode_to_utf8( cat_name )
            self.lock_ui(u"Creating category %s ..." % cat_name)
            cat_id = None
            try:
                cat_id = WordMobi.blog.newCategory(wpc)
            except:
                note(u"Impossible to create category %s." % cat_name,"error")
                
            self.unlock_ui()
            if cat_id is not None:
                self.update()
        self.refresh()

    def refresh(self):
        BaseTabWin.refresh(self)
        if len( self.headlines ) == 0:
            self.headlines = [ u"<empty>" ]
            WordMobi.categories = [ { 'categoryName':"Uncategorized", 'categoryId':'1', 'parentId':'0' } ]
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        self.body.set_list( self.headlines, self.last_idx )
        
class WordMobi(object):
    db = None
    proxy = None
    blog = None
    posts = []
    comments = []
    categories = [ { 'categoryName':"Uncategorized", 'categoryId':'1', 'parentId':'0' } ]

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
                        ( u"About", (
                          ( u"About", self.about_wordmobi),
                          ( u"Upgrade", self.upgrade_wordmobi)
                          )),
                        ( u"Exit", self.close_app )]


        tabs = [ PostTab(self.menu, self.close_app), CommentTab(self.menu, self.close_app), CategoryTab(self.menu, self.close_app) ]
        labels = [ u"Posts", u"Comments", u"Categories" ]
        BaseTabWin.register_tabs(  tabs, labels )        
        
        self.sel_access_point()
        self.refresh()

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
        ny = popup_menu( [u"Yes", u"No"], u"Exit ?" )
        if ny is not None:
            if ny == 0:
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

        BaseTabWin.restore_tabs()
        BaseTabWin.tabs['TABS'][0].refresh()
        return True
            
    def config_wordmobi(self):
        BaseTabWin.disable_tabs()    
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
        BaseTabWin.restore_tabs()
        BaseTabWin.tabs['TABS'][0].refresh()
        return True
    
    def config_network(self):
        BaseTabWin.disable_tabs()
        self.dlg = ProxySettings( self.config_network_cbk,\
                                  WordMobi.db["proxy_enabled"], \
                                  WordMobi.db["proxy_addr"], \
                                  int(WordMobi.db["proxy_port"]), \
                                  WordMobi.db["proxy_user"], \
                                  WordMobi.db["proxy_pass"])
        self.dlg.run()
        
    def about_wordmobi(self):
        def exit_about():
            BaseTabWin.restore_tabs()
            BaseTabWin.tabs['TABS'][0].refresh()
        BaseTabWin.disable_tabs()
        app.title = u"About"
        app.exit_key_handler = exit_about
        about = [ ( u"Wordmobi %s" % __version__, u"A Wordpress client" ),\
                  ( u"Author", u"Marcelo Barros de Almeida"), \
                  ( u"Email", u"marcelobarrosalmeida@gmail.com"), \
                  ( u"Source code", u"http://wordmobi.googlecode.com"), \
                  ( u"Blog", u"http://wordmobi.wordpress.com"), \
                  ( u"License", u"GNU GPLv3"), \
                  ( u"Warning", u"Use at your own risk") ]
        app.body = Listbox( about, lambda: None )
        app.menu = [ (u"Close", exit_about )]
        
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

    def upgrade_wordmobi(self):
        if WordMobi.db["proxy_enabled"] == u"True" and len(WordMobi.db["proxy_user"]) > 0:
            note(u"Proxy authentication not supported for this feature","info")
            return

        t = app.title
        app.menu = []
        BaseTabWin.disable_tabs()
        
        url = "http://code.google.com/p/wordmobi/wiki/LatestVersion"
        local_file = "web_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
        local_file = os.path.join(DEFDIR, "cache", local_file)

        app.title = u"Checking update page..."
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

                        app.title = u"Downloading ..."
                        ok = True
                        try:
                            urllib.urlretrieve( file_url, local_file )
                        except:
                            note(u"Impossible to download %s" % sis_name, "error")
                            ok = False

                        if ok:
                            note(u"%s downloaded in e:\\wordmobi\\updates. Please, install it." % sis_name, "info")
                            #app.title = u"Installing..."
                            #global viewer
                            #viewer = Content_handler( lambda: None )
                            #try:
                            #    viewer.open_standalone( local_file )
                            #except:
                            #    note(u"Impossible to open %s" % local_file,"error")
            else:
                note(u"Upgrade information missing.","error")

        app.title = t
        BaseTabWin.restore_tabs()
        BaseTabWin.tabs['TABS'][0].refresh()
        
    def run(self):
        old_title = app.title
        BaseTabWin.tabs['TABS'][0].refresh()
        self.lock.wait()
        self.clear_cache()
        app.set_tabs( [], None )
        app.title = old_title
        app.menu = []
        app.body = None
        app.set_exit()

if __name__ == "__main__":

    wm = WordMobi()
    wm.run()
