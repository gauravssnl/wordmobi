# -*- coding: utf-8 -*-
import e32
from appuifw import *
from wmutil import *
import wordpresslib as wp

class CommentsDetails(object):
    pass
    
class ViewComments(object):
    def __init__(self,
                 cbk,
                 blog,
                 comments,
                 app_title=u"View comment"):

        self.cbk = cbk
        self.blog = blog
        self.comments = comments
        self.app_title = app_title        
        self.ui_lock = False
        
        self.body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        self.last_idx = 0
        self.menu = [ ( u"New", self.comment_new ), ( u"Update list", self.comment_update ),( u"Close", self.close_app ) ]

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
        self.cbk()

    def comment_update(self):
        pass
    
    def comment_new(self):
        pass

    def comment_reply(self,idx):
        pass    
    
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
        
        comment = wp.WordPressCommentEdit()
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
                self.comment_reply(idx)
            elif op == 2:
                self.comment_delete(idx)
            elif op == 3:
                self.comment_approve(idx)
        
    def run(self):
        self.refresh()
