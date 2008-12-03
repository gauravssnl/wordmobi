# -*- coding: utf-8 -*-
import e32
from appuifw import *
from wmutil import *
import wordpresslib as wp

class CommentContents(object):
    def __init__(self, cbk, contents=u""):
        self.cbk = cbk
        self.cancel = False

        self.body = Text( contents )
        self.body.focus = True
        self.body.set_pos( 0 )

        self.refresh()
    
    def refresh(self):            
        app.menu = [( u"Cancel", self.cancel_app )]        

        app.exit_key_handler = self.close_app
        app.title = u"New comment"

        app.body = self.body
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            self.cbk( self.body.get() )
        else:
            self.cbk( None )
            
    def run(self):
        self.refresh()

class NewComment(object):
    def __init__(self,
                 cbk,
                 name=u"",
                 email=u"",
                 website=u"http://",                 
                 contents=u""):
        
        self.cbk = cbk
        self.name = name
        self.email = email
        self.website = website
        self.contents = contents
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.cancel = False
        self.last_idx = 0
        self.menu = [ ( u"Cancel", self.cancel_app ) ]
        self.app_title = u"New Comment"

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = self.app_title

        self.lst_values = [ (u"Name", self.name ), \
                            (u"Email", self.email), \
                            (u"Website", self.website), \
                            (u"Contents", self.contents[:50]) ]

        app.body = self.body
        app.body.set_list( self.lst_values, self.last_idx )
        app.menu = self.menu        

    def lock_ui(self,msg = u""):
        self.ui_lock = True
        app.menu = []
        if msg:
            app.title = msg

    def unlock_ui(self):
        self.ui_lock = False
        app.menu = self.menu
        app.title = self.title

    def ui_is_locked(self):
        return self.ui_lock
        
    def cancel_app(self):
        self.cancel = True
        self.close_app()
        
    def close_app(self):
        if not self.cancel:
            ny = popup_menu( [u"Yes", u"No"], u"Send comment ?")
            if ny == 0:            
                if self.cbk( (self.name, self.email, self.website, self.contents) ) == False:
                    self.refresh()
            else:
                self.cbk( None )                    
        else:
            self.cbk( None )
        
    def update_name(self):
        name = query(u"Name:","text", self.name)
        if name is not None:
            self.name = name
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
        
    def update_contents(self):
        def cbk( txt ):
            if txt is not None:
                self.contents = txt
            self.refresh()
        self.dlg = CommentContents( cbk, self.contents )
        self.dlg.run()

    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update( app.body.current() )
            
    def update(self,idx):
        self.last_idx = idx
        updates = ( self.update_name, self.update_email, \
                    self.update_website, self.update_contents )
        if idx < len(updates):
            updates[idx]()

    def run(self):
        self.refresh()
    
class Comments(object):
    def __init__(self,
                 cbk,
                 blog,
                 comments,
                 app_title=u"Comments"):

        self.cbk = cbk
        self.blog = blog
        self.comments = comments
        self.app_title = app_title        
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.last_idx = 0
        self.menu = [ ( u"New", self.comment_reply ), \
                      ( u"Update list", self.comment_update ), \
                      ( u"Close", self.close_app ) ]

    def refresh(self):
        app.exit_key_handler = self.close_app
        app.title = self.app_title

        self.lst_values = []
        for comment in self.comments:
            (y, mo, d, h, m, s) = parse_iso8601( comment['date_created_gmt'].value )
            if comment['status'] == 'approve':
                status = ''
            else:
                status = 'Wait. moder.'
            line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,status,utf8_to_unicode( comment['author'] ))
            line2 = utf8_to_unicode(comment['content'])
            self.lst_values.append( (line1, line2) )

        app.body = self.body
        app.body.set_list( self.lst_values, self.last_idx )
        app.menu = self.menu        

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
        # TODO: need to update post info if any comment is changed here !!!!
        # !!!!!!!!!!!!!
        self.cbk()

    def comment_update(self):
        pass

    def comment_reply(self,parent=0):
        def cbk( txt ):
            if txt is not None:
                pass
            self.refresh()
        self.dlg = NewComment( cbk )
        self.dlg.run() 
    
    def comment_view(self,idx):
        pass    

    def comment_delete(self,idx):
        ny = popup_menu( [u"No", u"Yes"], u"Delete comment ?")
        if ny == 1:
            self.lock_ui(u"Deleting comment %s" % utf8_to_unicode( self.comments[idx]['content'][:15] ))

            try:
                self.blog.deleteComment(self.comments[idx]['comment_id'])
            except:
                note(u"Impossible to delete the comment. Try again.","error")
                self.unlock_ui()
                return

            del self.comments[idx]
            note(u"Comment deleted.","info")
            self.unlock_ui()
            self.refresh()
    
    def comment_approve(self,idx):
        self.lock_ui(u"Approving comment %s" % utf8_to_unicode( self.comments[idx]['content'][:15] ))
        
        comment = wp.WordPressEditComment()
        comment.status = 'approve'
        comment.date_created_gmt = self.comments[idx]['date_created_gmt']
        comment.content = self.comments[idx]['content']
        comment.author = self.comments[idx]['author']
        comment.author_url = self.comments[idx]['author_url']
        comment.author_email = self.comments[idx]['author_email']

        try:
            self.blog.editComment(self.comments[idx]['comment_id'], comment)
        except:
            note(u"Impossible to approve the comment. Try again.","error")
            self.unlock_ui()
            return

        self.comments[idx]['status'] = 'approve'
        note(u"Comment approved.","info")
        self.unlock_ui()
        self.refresh()
        
    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update_value( app.body.current() )

    def update_value(self,idx):
        self.last_idx = idx
        menu_items = [u"View/Edit", u"Reply", u"Delete"]
        if self.comments[idx]['status'] != 'approve':
            menu_items.append( u"Approve" )
            
        op = popup_menu( menu_items, u"Comment:")
        if op is not None:
            if op == 0:
                self.comment_view(idx)
            elif op == 1:
                self.comment_reply(self.comments[idx]['parent'])
            elif op == 2:
                self.comment_delete(idx)
            elif op == 3:
                self.comment_approve(idx)
        
    def run(self):
        self.refresh()
