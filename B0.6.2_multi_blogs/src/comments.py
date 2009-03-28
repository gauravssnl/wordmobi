# -*- coding: utf-8 -*-
import time
import e32
import key_codes
import wordpresslib as wp
from xmlrpclib import DateTime
from appuifw import *
from wmutil import *
from window import Dialog
from persist import DB
from wpwrapper import BLOG
from wmlocale import LABELS

__all__ = [ "NewComment", "EditComment", "Comments" ]

class CommentContents(Dialog):

    PARAGRAPH_SEPARATOR = u"\u2029"

    def __init__(self, cbk, contents=u""):
        body = Text( self.commment_to_text(contents) )
        body.focus = True
        body.set_pos( 0 )

        Dialog.__init__(self, cbk, LABELS.loc.cm_info_cmt_contents, body,
                        [(LABELS.loc.cm_menu_canc, self.cancel_app)])

        self.refresh()

    def commment_to_text(self,msg):
        return msg.replace(u"\n",CommentContents.PARAGRAPH_SEPARATOR)
    
    def text_to_comment(self,msg):
        return msg.replace(CommentContents.PARAGRAPH_SEPARATOR,u"\n")

class NewComment(Dialog):
    def __init__(self,
                 cbk,
                 comment_idx,
                 post_id,
                 post_title,
                 realname=u"",
                 email=u"",
                 website=u"http://",                 
                 contents=u""):

        self.comment_idx = comment_idx
        self.post_id = post_id
        self.post_title = post_title
        self.realname = realname
        self.email = email
        self.website = website
        self.contents = contents
        self.last_idx = 1
        
        body = Listbox( [ (u"",u"") ], self.update_value_check_lock )
        menu = [ ( LABELS.loc.cm_menu_canc, self.cancel_app ) ]
        Dialog.__init__(self, cbk, LABELS.loc.cm_info_new_cmt, body, menu)
        self.bind(key_codes.EKeyLeftArrow, self.close_app)
        self.bind(key_codes.EKeyRightArrow, self.update_value_check_lock)

    def refresh(self):
        Dialog.refresh(self) # must be called *before*

        lst_values = [ (LABELS.loc.cm_menu_pstt, self.post_title), \
                       (LABELS.loc.cm_menu_cont, self.contents[:50]), \
                       (LABELS.loc.cm_menu_name, self.realname ), \
                       (LABELS.loc.cm_menu_mail, self.email), \
                       (LABELS.loc.cm_menu_webs, self.website) ]

        app.body.set_list( lst_values, self.last_idx )      

    def close_app(self):
        if not self.cancel:
            ny = popup_menu( [LABELS.loc.gm_yes, LABELS.loc.gm_no], LABELS.loc.cm_pmenu_send_cmt)
            if ny is None:
                return
            if ny == 1:
                self.cancel = True

        Dialog.close_app(self)    

    def show_post_title(self):
        note( self.post_title, "info" )
        
    def update_contents(self):
        def cbk():
            if not self.dlg.cancel :
                self.contents = self.dlg.text_to_comment( self.dlg.body.get() )
            self.refresh()
            return True
        self.dlg = CommentContents( cbk, self.contents )
        self.dlg.run()
        
    def update_name(self):
        realname = query(LABELS.loc.cm_menu_name,"text", self.realname)
        if realname is not None:
            self.realname = realname
        self.refresh()

    def update_email(self):
        email = query(LABELS.loc.cm_menu_mail,"text", self.email)
        if email is not None:
            self.email = email
        self.refresh()

    def update_website(self):
        website = query(LABELS.loc.cm_menu_webs,"text", self.website)
        if website is not None:
            self.website = website
        self.refresh()
        
    def update_value_check_lock(self):
        if self.ui_is_locked() == False:
            self.update( app.body.current() )
            
    def update(self,idx):
        self.last_idx = idx
        updates = ( self.show_post_title,
                    self.update_contents,
                    self.update_name,
                    self.update_email,
                    self.update_website )
        if idx < len(updates):
            updates[idx]()

class EditComment(NewComment):
    def __init__(self,
                 cbk,
                 comment_idx,
                 post_id,
                 post_title,
                 realname=u"",
                 email=u"",
                 website=u"http://",                 
                 contents=u""):

        NewComment.__init__(self, cbk, comment_idx, post_id, post_title,
                            realname, email, website, contents)
        self.set_title(LABELS.loc.cm_info_edit_cmt)

    def close_app(self):
        if not self.cancel:
            ny = popup_menu( [LABELS.loc.gm_no, LABELS.loc.gm_yes], LABELS.loc.cm_pmenu_updt_cmt)
            if ny is None:
                return
            if ny == 0:
                self.cancel = True
        Dialog.close_app(self)
        
class Comments(Dialog):
    def __init__(self,cbk):
        self.status_list = { LABELS.loc.cm_list_any:"",
                             LABELS.loc.cm_list_spam:"spam",
                             LABELS.loc.cm_list_moderated:"approve",
                             LABELS.loc.cm_list_unmoderated:"hold" }
        self.last_idx = 0
        self.headlines = []
        body = Listbox( [ (u"", u"") ], self.check_popup_menu )
        self.menu_items = [( LABELS.loc.cm_menu_updt, self.update ),
                           ( LABELS.loc.cm_menu_view, self.contents ),
                           ( LABELS.loc.cm_menu_dele, self.delete ),
                           ( LABELS.loc.cm_menu_cnew, self.new ) ]
        menu = self.menu_items + [( LABELS.loc.cm_menu_clos, self.close_app )]
        Dialog.__init__(self, cbk, LABELS.loc.wm_menu_comm, body, menu)

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
            self.set_title( LABELS.loc.cm_info_cat_pos % (p+1,m) )
            #self.tooltip.show( self.headlines[p][1], (30,30), 2000, 0.25 )

    def key_down(self):
        if not self.ui_is_locked():
            p = app.body.current() + 1
            m = len( self.headlines )
            if p >= m:
                p = 0
            self.set_title( LABELS.loc.cm_info_cat_pos % (p+1,m) )
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
        if BLOG.comments:
            if BLOG.comments[app.body.current()]['status'] != 'approve':
                menu.append(LABELS.loc.cm_list_approve)
                cbk.append(self.moderate)            
        op = popup_menu(menu, LABELS.loc.cm_pmenu_comts)
        if op is not None:
            self.last_idx = app.body.current()
            cbk[op]()

    def moderate(self):
        t = self.get_title()
        idx = app.body.current()
        self.lock_ui(LABELS.loc.cm_info_aprv_cmt % utf8_to_unicode( BLOG.comments[idx]['content'][:15] ))
        BLOG.approve_comment(idx)
        self.unlock_ui()
        self.set_title( t )
        self.refresh()
        
    def update(self, post_idx=None):
        k = self.status_list.keys()
        item = popup_menu( k, LABELS.loc.cm_pmenu_cmt_status)
        if item is None:
            return False
        comment_status = k[item]

        t = self.get_title()
        if not BLOG.posts:
            self.lock_ui(LABELS.loc.cm_info_downld_pt)
            upd = BLOG.update_posts_and_cats()
            self.set_title( t )
            self.unlock_ui()
            if not upd:
                self.refresh()
                return False

        if post_idx is None:
            comment_set = popup_menu( [ LABELS.loc.cm_list_one_post,
                                        LABELS.loc.cm_list_all_posts ],
                                      LABELS.loc.cm_pmenu_updt_for)
            if comment_set is None:
                return False
            
            if comment_set == 0:
                self.set_title( LABELS.loc.cm_info_which_post )
                post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in BLOG.posts ], search_field=1)
                self.set_title( t )
                if post_idx is None or post_idx == -1:
                    return False
            else:
                post_idx = -1

        self.lock_ui()
        upd = self.update_comment(post_idx, comment_status)
        self.set_title( LABELS.loc.wm_menu_comm )
        self.unlock_ui()
        self.refresh()
        
        return upd

    def update_comment(self, post_idx, comment_status):
        BLOG.comments = []        
        if post_idx == -1:
            np = len(BLOG.posts)
            for n in range(np):
                self.set_title(LABELS.loc.cm_info_downld_cmts % (n+1,np))
                if not BLOG.get_comment(n, self.status_list[comment_status]):
                    yn = popup_menu( [ LABELS.loc.gm_yes, LABELS.loc.gm_no ],
                                     LABELS.loc.cm_pmenu_downld_fail)
                    if yn is not None:
                        if yn == 0:
                            continue
                    return False
        else:
            self.set_title(LABELS.loc.cm_info_downld_cmt)
            if not BLOG.get_comment(post_idx, self.status_list[comment_status]):
                return False

        if not BLOG.comments:
            note(LABELS.loc.cm_info_no_cmts_st % comment_status,"info")
            return False
  
        return True        
            
    def delete(self):
        if not BLOG.comments:
            note( LABELS.loc.cm_info_udt_cmts_lst, "info" )
            return
        
        ny = popup_menu( [LABELS.loc.gm_no, LABELS.loc.gm_yes], LABELS.loc.cm_pmenu_del_cmt)
        if ny == 1:
            idx = app.body.current()
            self.lock_ui(LABELS.loc.cm_info_del_cmt % utf8_to_unicode( BLOG.comments[idx]['content'][:15] ))
            BLOG.delete_comment(idx)
            
            self.unlock_ui()
            self.refresh()
            
    def new_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui(LABELS.loc.cm_info_upld_cmt)
            ok = BLOG.new_comment(self.dlg.post_id,
                                           self.dlg.email,
                                           self.dlg.realname,
                                           self.dlg.website,
                                           self.dlg.contents)
            self.unlock_ui()
            
            if not ok:
                return False
        self.set_title(LABELS.loc.wm_menu_comm)
        self.refresh()
        return True
    
    def new(self):
        t = self.get_title()
        if not BLOG.comments:
            # no comments ... user need to select a post to add the comment
            if not BLOG.posts:
                self.lock_ui(LABELS.loc.cm_info_downld_pt)
                upd = BLOG.update_posts_and_cats()
                self.set_title( t )
                self.unlock_ui()
                if not upd:
                    return False
        
            self.set_title(LABELS.loc.cm_info_which_post)
            post_idx = selection_list( [ utf8_to_unicode( p['title'] )[:70] for p in BLOG.posts ], search_field=1)
            # idx may be -1 if list is empty and user press OK... strange ... why not None ?
            if post_idx is None or post_idx == -1:
                return False
            post_id = BLOG.posts[post_idx]['postid']
            post_title = BLOG.posts[post_idx]['title']
        else:
            comment_idx = self.body.current()
            post_id = BLOG.comments[comment_idx]['post_id']
            post_title = BLOG.comments[comment_idx]['post_title']
            
        self.dlg = NewComment( self.new_cbk,
                               0,
                               post_id,
                               utf8_to_unicode(post_title))
        self.dlg.run()
            
    def contents_cbk(self):
        if not self.dlg.cancel:
            self.lock_ui(LABELS.loc.cm_info_updt_cmt)
            ok = BLOG.edit_comment(self.dlg.comment_idx,
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
        if not BLOG.comments:
            note(LABELS.loc.cm_info_udt_cmts_lst, "info" )
            return
        idx = self.body.current()
        self.dlg = EditComment( self.contents_cbk, \
                                idx, \
                                utf8_to_unicode( BLOG.comments[idx]['post_id']), \
                                utf8_to_unicode( BLOG.comments[idx]['post_title']), \
                                utf8_to_unicode( BLOG.comments[idx]['author']), \
                                utf8_to_unicode( BLOG.comments[idx]['author_email']), \
                                utf8_to_unicode( BLOG.comments[idx]['author_url']), \
                                utf8_to_unicode( BLOG.comments[idx]['content']))
        self.dlg.run()        

    def translate_status(self, status):
        s = LABELS.loc.cm_info_undef
        for k,v in self.status_list.items():
            if v == status:
                s = k
                break
        return s
    
    def refresh(self):
        Dialog.refresh(self) # must be called *before* 

        if not BLOG.comments:
            self.headlines = [ (LABELS.loc.cm_info_empty, LABELS.loc.cm_info_udt_cmts_lst) ]
        else:
            self.headlines = []
            for c in BLOG.comments:
                (y, mo, d, h, m, s) = parse_iso8601( c['date_created_gmt'].value )
                line1 = u"%d/%s %02d:%02d %s (%s)" % (d,MONTHS[mo-1],h,m,self.translate_status(c['status']),\
                                                      utf8_to_unicode( c['author'] ))
                line2 = utf8_to_unicode( c['content'] )
                self.headlines.append( ( line1 , line2 ) )
                               
        self.last_idx = min( self.last_idx, len(self.headlines)-1 ) # avoiding problems after removing
        app.body.set_list( self.headlines, self.last_idx )
