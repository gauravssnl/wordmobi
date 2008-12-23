# -*- coding: utf-8 -*-
import time
import e32
import key_codes
import wordpresslib as wp
from xmlrpclib import DateTime
from appuifw import *
from wmutil import *
from window import Dialog
import wordmobi

__all__ = [ "NewComment", "EditComment", "Comments" ]

class CommentContents(Dialog):

    PARAGRAPH_SEPARATOR = u"\u2029"

    def __init__(self, cbk, contents=u""):
        body = Text( self.commment_to_text(contents) )
        body.focus = True
        body.set_pos( 0 )

        Dialog.__init__(self, cbk, u"Comment Contents", body, [(u"Cancel", self.cancel_app)])

        self.refresh()

    def commment_to_text(self,msg):
        return msg.replace(u"\n",CommentContents.PARAGRAPH_SEPARATOR)
    
    def text_to_comment(self,msg):
        return msg.replace(CommentContents.PARAGRAPH_SEPARATOR,u"\n")

class NewComment(Dialog):
    def __init__(self,
                 cbk,
                 post_id,
                 realname=u"",
                 email=u"",
                 website=u"http://",                 
                 contents=u""):
        
        self.post_id = post_id
        self.realname = realname
        self.email = email
        self.website = website
        self.contents = contents
        self.last_idx = 0
        
        body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        menu = [ ( u"Cancel", self.cancel_app ) ]
        Dialog.__init__(self, cbk, u"New Comment", body, menu)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value_check_lock)

    def refresh(self):
        Dialog.refresh(self) # must be called *before*

        lst_values = [ (u"Contents", self.contents[:50]), \
                       (u"Name", self.realname ), \
                       (u"Email", self.email), \
                       (u"Website", self.website) ]

        app.body.set_list( lst_values, self.last_idx )      

    def close_app(self):
        if not self.cancel:
            ny = popup_menu( [u"Yes", u"No"], u"Send comment ?")
            if ny is None:
                return
            if ny == 1:
                self.cancel = True

        Dialog.close_app(self)    

    def update_contents(self):
        def cbk():
            if not self.dlg.cancel :
                self.contents = self.dlg.text_to_comment( self.dlg.body.get() )
            self.refresh()
            return True
        self.dlg = CommentContents( cbk, self.contents )
        self.dlg.run()
        
    def update_name(self):
        realname = query(u"Name:","text", self.realname)
        if realname is not None:
            self.realname = realname
        self.refresh()

    def update_email(self):
        email = query(u"Email:","text", self.email)
        if email is not None:
            self.email = email
        self.refresh()

    def update_website(self):
        website = query(u"Website:","text", self.website)
        if website is not None:
            self.website = website
        self.refresh()
        
    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update( app.body.current() )
            
    def update(self,idx):
        self.last_idx = idx
        updates = ( self.update_contents, self.update_name, self.update_email, self.update_website )
        if idx < len(updates):
            updates[idx]()

class EditComment(NewComment):
    def __init__(self,
                 cbk,
                 idx,
                 realname=u"",
                 email=u"",
                 website=u"http://",                 
                 contents=u""):

        self.idx = idx
        NewComment.__init__(self, cbk, 0, realname, email, website, contents)
        self.set_title(u"Edit Comment")

    def close_app(self):
        if not self.cancel:
            ny = popup_menu( [u"No", u"Yes"], u"Update comment ?")
            if ny is None:
                return
            if ny == 0:
                self.cancel = True
        Dialog.close_app(self)
        
class Comments(Dialog):
    def __init__(self,cbk):
        self.status_list = { u"Any":"", u"Spam":"spam", u"Moderated":"approve", u"Unmoderated":"hold" }
        self.last_idx = 0
        self.headlines = []
        body = Listbox( [ (u"", u"") ], self.check_popup_menu )
        self.menu_items = [( u"Update", self.update ),
                           ( u"View/Edit", self.contents ),
                           ( u"Delete", self.delete ),
                           ( u"Create new/Reply", self.new ) ]
        menu = self.menu_items + [( u"Close", self.close_app )]
        Dialog.__init__(self, cbk, u"Comments", body, menu)

        self.bind(key_codes.EKeyUpArrow, self.key_up)
        self.bind(key_codes.EKeyDownArrow, self.key_down)
        self.bind(key_codes.EKeyLeftArrow, self.key_left)
        self.bind(key_codes.EKeyRightArrow, self.key_right)

    def key_left(self):
        if not self.ui_is_locked():
            self.close_app()
            
    def key_up(self):
        if not self.ui_is_locked():
            p = app.body.current() - 1
            m = len( self.headlines )
            if p < 0:
                p = m - 1
            self.set_title( u"[%d/%d] Comments" % (p+1,m) )
            #self.tooltip.show( self.headlines[p][1], (30,30), 2000, 0.25 )

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( u"[%d/%d] Comments" % (p+1,m) )
            #self.tooltip.show( self.headlines[p][1], (30,30), 2000, 0.25 )

    def key_right(self):
        if not self.ui_is_locked():
            self.contents()

    def check_popup_menu(self):
        if not self.ui_is_locked():
            self.popup_menu()

    def popup_menu(self):
        menu = map( lambda x: x[0], self.menu_items )
        cbk = map( lambda x: x[1], self.menu_items )
        if wordmobi.BLOG.comments:
            if wordmobi.BLOG.comments[app.body.current()]['status'] != 'approve':
                menu.append( u"Approve" )
                cbk.append( self.moderate )            
        op = popup_menu( menu , u"Comments:")
        if op is not None:
            self.last_idx = app.body.current()
            cbk[op]()

    def moderate(self):
        t = self.get_title()
        idx = app.body.current()
        self.lock_ui(u"Approving comment %s" % utf8_to_unicode( wordmobi.BLOG.comments[idx]['content'][:15] ))
        wordmobi.BLOG.approve_comment(idx)
        self.unlock_ui()
        self.set_title( t )
        self.refresh()
        
    def update(self, post_idx=None):
        k = self.status_list.keys()
        item = popup_menu( k, u"Comment status:")
        if item is None:
            return False
        comment_status = k[item]

        t = self.get_title()
        if not wordmobi.BLOG.posts:
            self.lock_ui(u"Downloading post titles..." )
            upd = wordmobi.BLOG.update_posts()
            self.set_title( t )
            self.unlock_ui()
            if not upd:
                return False

        if post_idx is None:
            comment_set = popup_menu( [ u"One post", u"All posts", ], u"Upd comments for?")
            if comment_set is None:
                return False
            
            if comment_set == 0:
                self.set_title( u"Which post?" )
                post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in wordmobi.BLOG.posts ], search_field=1)
                self.set_title( t )
                if post_idx is None or post_idx == -1:
                    return False
            else:
                post_idx = -1

        self.lock_ui()
        
        upd = self.update_comment(post_idx, comment_status)
        
        self.set_title( u"Comments" )
        self.unlock_ui()
        self.refresh()
        
        return upd

    def update_comment(self, post_idx, comment_status):
        wordmobi.BLOG.comments = []        
        if post_idx == -1:
            np = len(wordmobi.BLOG.posts)
            for n in range(np):
                self.set_title(u"[%d/%d] Downloading comments ..." % (n+1,np))
                if not wordmobi.BLOG.get_comment(n, self.status_list[comment_status]):
                    yn = popup_menu( [ u"Yes", u"No" ], u"Downl. Failed ! Continue?")
                    if yn is not None:
                        if yn == 0:
                            continue
                    return False
        else:
            self.set_title(u"Downloading comments ...")
            if not wordmobi.BLOG.get_comment(post_idx, self.status_list[comment_status]):
                return False

        if not wordmobi.BLOG.comments:
            note(u"No comments with status %s." % comment_status,"info")
            return False
  
        return True        
            
    def delete(self):
        if not wordmobi.BLOG.comments:
            note( u"Please, update the comment list.", "info" )
            return
        
        ny = popup_menu( [u"No", u"Yes"], u"Delete comment ?")
        if ny == 1:
            idx = app.body.current()
            self.lock_ui(u"Deleting comment %s" % utf8_to_unicode( wordmobi.BLOG.comments[idx]['content'][:15] ))
            wordmobi.BLOG.delete_comment(idx)
            self.unlock_ui()
            self.refresh()
            
    def new_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui(u"Uploading comment ..." )
            ok = wordmobi.BLOG.new_comment(self.dlg.post_id,
                                           self.dlg.email,
                                           self.dlg.realname,
                                           self.dlg.website,
                                           self.dlg.contents)
            self.unlock_ui()
            
            if not ok:
                return False
        self.set_title(u"Comments")
        self.refresh()
        return True
    
    def new(self):
        t = self.get_title()
        if not wordmobi.BLOG.comments:
            # no comments ... user need to select a post to add the comment
            if not wordmobi.BLOG.posts:
                self.lock_ui(u"Downloading post titles..." )
                upd = wordmobi.BLOG.update_posts()
                self.set_title( t )
                self.unlock_ui()
                if not upd:
                    return False
        
            self.set_title(u"For which post?")
            post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in wordmobi.BLOG.posts ], search_field=1)
            # idx may be -1 if list is empty and user press OK... strange ... why not None ?
            if post_idx is None or post_idx == -1:
                return False
            post_id = wordmobi.BLOG.posts[post_idx]['postid']
        else:
            comment_idx = self.body.current()
            post_id = wordmobi.BLOG.comments[comment_idx]['post_id']
            
        self.dlg = NewComment( self.new_cbk,
                               post_id,
                               wordmobi.DB['realname'],
                               wordmobi.DB['email'],
                               wordmobi.DB['blog'],
                               u"")
        self.dlg.run()
            
    def contents_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui(u"Updating comment ..." )
            ok = wordmobi.BLOG.edit_comment(self.dlg.post_id,
                                            self.dlg.email,
                                            self.dlg.realname,
                                            self.dlg.website,
                                            self.dlg.contents)
            self.unlock_ui()
            
            if not ok:
                return False
            
        self.refresh()
        return True
    
    def contents(self):
        if not wordmobi.BLOG.comments:
            note( u"Please, update the comment list.", "info" )
            return
        
        idx = self.body.current()
        self.dlg = EditComment( self.contents_cbk, idx, \
                                utf8_to_unicode( wordmobi.BLOG.comments[idx]['author'] ), \
                                utf8_to_unicode( wordmobi.BLOG.comments[idx]['author_email'] ), \
                                utf8_to_unicode( wordmobi.BLOG.comments[idx]['author_url'] ), \
                                utf8_to_unicode( wordmobi.BLOG.comments[idx]['content'] ))
        self.dlg.run()        

    def translate_status(self, status):
        s = "Undef"
        for k,v in self.status_list.items():
            if v == status:
                s = k
                break
        return s
    
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 

        if not wordmobi.BLOG.comments:
            self.headlines = [ (u"<empty>", u"Please, update the comment list") ]
        else:
            self.headlines = []
            for c in wordmobi.BLOG.comments:
                (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']),\
                                                      utf8_to_unicode( c['author'] ))
                line2 = utf8_to_unicode( c['content'] )
                self.headlines.append( ( line1 , line2 ) )
                               
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        app.body.set_list( self.headlines, self.last_idx )
