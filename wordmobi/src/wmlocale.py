# -*- coding: utf-8 -*-

__all__ = [ "Locale" ]

class Loc_Data(object):
    "Translation data holder"
    pass

class Default(object):
    "Default language support"
    def __init__(self):
        self.loc = Loc_Data()
        # Wordmobi main menu
        self.loc.wm_menu_post = u"Posts"
        self.loc.wm_menu_comm = u"Comments"
        self.loc.wm_menu_tags = u"Tags"
        self.loc.wm_menu_cats = u"Categories"
        self.loc.wm_menu_sets = u"Settings"
        self.loc.wm_menu_upgr = u"Upgrade"
        self.loc.wm_menu_abou = u"About"
        self.loc.wm_menu_exit = u"Exit"

        # Wordmobi error messages
        self.loc.wm_err_not_supp = u"Not supported yet."
        self.loc.wm_err_no_proxy = u"Proxy authentication not supported for this feature."
        self.loc.wm_err_upd_page = u"Impossible to access update page %s"
        self.loc.wm_err_downld_fail = u"Impossible to download %s"
        self.loc.wm_err_upd_info = u"Upgrade information missing."
        self.loc.wm_err_cache_cleanup = u"Not all files in %s could be removed. Try to remove them later."

        # Wordmobi info messages
        self.loc.wm_info_check_updt = u"Checking update page..."
        self.loc.wm_info_ver_is_updt = u"Your version is already updated."
        self.loc.wm_info_downloading = u"Downloading ..."
        # do not translate "%supdates"
        self.loc.wm_info_downld_ok = u"%s downloaded in %supdates. Please, install it."

        # Wordmobi popup menus
        self.loc.wm_pmenu_download = "Download %s ?"
        self.loc.wm_pmenu_exit = u"Exit ?"

        # General messages
        self.loc.gm_yes = u"Yes"
        self.loc.gm_no = u"No"

        # About main menu
        self.loc.ab_menu_wordmobi_defi_val = u"A Wordpress client"
        self.loc.ab_menu_wordmobi_auth = u"Author"
        self.loc.ab_menu_wordmobi_mail = u"Email"
        self.loc.ab_menu_wordmobi_srcc = u"Source code"
        self.loc.ab_menu_wordmobi_blog = u"Blog"
        self.loc.ab_menu_wordmobi_lics = u"License"
        self.loc.ab_menu_wordmobi_warn = u"Warning"
        self.loc.ab_menu_wordmobi_warn_val = u"Use at your own risk"

        # Categories main menu
        self.loc.ca_menu_updt = u"Update"
        self.loc.ca_menu_dele = u"Delete"
        self.loc.ca_menu_cnew = u"Create new"
        self.loc.ca_menu_clos = u"Close"

        # Categories popup menu
        self.loc.ca_pmenu_cats = u"Categories:"
        self.loc.ca_pmenu_delete = u"Delete %s ?"

        # Categories info messages
        self.loc.ca_info_cat_pos = u"[%d/%d] Categories"
        self.loc.ca_info_downld_cats = u"Downloading categories..."
        self.loc.ca_info_del_cat = u"Deleting category %s ..."
        self.loc.ca_info_create_cat = u"Creating category %s ..."

        # categories queries
        self.loc.ca_query_cat_name = u"Category name:"

        # Comments main menu
        self.loc.cm_menu_updt = u"Update"
        self.loc.cm_menu_view = u"View/Edit"
        self.loc.cm_menu_dele = u"Delete"
        self.loc.cm_menu_cnew = u"Create new/Reply"
        self.loc.cm_menu_clos = u"Close"
        self.loc.cm_menu_canc = u"Cancel"
        self.loc.cm_menu_pstt = u"Post title"
        self.loc.cm_menu_cont = u"Contents"
        self.loc.cm_menu_name = u"Name"
        self.loc.cm_menu_mail = u"Email"
        self.loc.cm_menu_webs = u"Website"

        # Comments lists
        self.loc.cm_list_any = u"Any"
        self.loc.cm_list_spam = u"Spam"
        self.loc.cm_list_moderated = u"Moderated"
        self.loc.cm_list_unmoderated = u"Unmoderated"
        self.loc.cm_list_one_post = u"One post"
        self.loc.cm_list_all_posts = u"All posts"

        # Comments info
        self.loc.cm_info_cat_pos = u"[%d/%d] Comments"
        self.loc.cm_info_aprv_cmt = u"Approving comment %s"
        self.loc.cm_info_downld_pt = u"Downloading post titles..."
        self.loc.cm_info_which_post = u"For which post?"
        self.loc.cm_info_downld_cmts = u"[%d/%d] Downloading comments ..."
        self.loc.cm_info_downld_cmt = u"Downloading comments ..."
        self.loc.cm_info_no_cmts_st = u"No comments with status '%s'."
        self.loc.cm_info_udt_cmts_lst = u"Please, update the comment list."
        self.loc.cm_info_del_cmt = u"Deleting comment %s"
        self.loc.cm_info_upld_cmt = u"Uploading comment ..."
        self.loc.cm_info_updt_cmt = u"Updating comment ..."
        self.loc.cm_info_undef = u"Undefined"
        self.loc.cm_info_empty = u"<empty>"
        self.loc.cm_info_cmt_contents = u"Comment Contents"
        self.loc.cm_info_new_cmt = u"New Comment"
        self.loc.cm_info_edit_cmt = u"Edit Comment"

        # Comments popup menu
        self.loc.cm_pmenu_cmt_status = u"Comment status:"
        self.loc.cm_pmenu_updt_for = u"Upd comments for?"
        self.loc.cm_pmenu_downld_fail = u"Downl. failed ! Continue?"
        self.loc.cm_pmenu_del_cmt = u"Delete comment ?"
        self.loc.cm_pmenu_send_cmt = u"Send comment ?"
        self.loc.cm_pmenu_updt_cmt = u"Update comment ?"
        self.loc.cm_pmenu_comts = u"Comments:"

        # Posts main menu
        self.loc.pt_menu_updt = u"Update"
        self.loc.pt_menu_view = u"View/Edit"
        self.loc.pt_menu_dele = u"Delete"
        self.loc.pt_menu_lstc = u"List Comments"
        self.loc.pt_menu_cnew = u"Create new"
        self.loc.pt_menu_clos = u"Close"
        self.loc.pt_menu_pict = u"Take a photo"
        self.loc.pt_menu_canc = u"Cancel"
        self.loc.pt_menu_text = u"Text"
        self.loc.pt_menu_refs = u"Links/images"
        self.loc.pt_menu_lsts = u"Lists"
        self.loc.pt_menu_revs = u"Revision"
        self.loc.pt_menu_prvw = u"Preview"
        self.loc.pt_menu_titl = u"Title"
        self.loc.pt_menu_cont = u"Contents"
        self.loc.pt_menu_cats = u"Categories"
        self.loc.pt_menu_imgs = u"Images"
        self.loc.pt_menu_pubs = u"Publish"
        
        # Posts lists
        self.loc.pt_list_320x240 = u"(320x240)"
        self.loc.pt_list_640x480 = u"(640x480)"
        self.loc.pt_list_fsh_auto = u"Auto"
        self.loc.pt_list_fsh_none = u"None"
        self.loc.pt_list_fsh_forc = u"Forced"
        self.loc.pt_list_loc_file = u"Local file"
        self.loc.pt_list_url = u"URL"
        self.loc.pt_list_ins_img = u"Insert"
        self.loc.pt_list_take_img = u"Take a photo"
        self.loc.pt_list_view_img = u"View/List"
        self.loc.pt_list_rem_img = u"Remove"
        
        # Posts info
        self.loc.pt_info_pst_pos = u"[%d/%d] Posts"
        self.loc.pt_info_downld_pt = u"Downloading post titles..."
        self.loc.pt_info_no_posts = u"No posts available."
        self.loc.pt_info_del_post = u"Deleting post..."
        self.loc.pt_info_post_del = u"Post deleted."
        self.loc.pt_info_updt_pst_lst = u"Please, update the post list."
        self.loc.pt_info_downld_post = u"Downloading post..."
        self.loc.pt_info_empty = u"<empty>"
        self.loc.pt_info_pict = u"Take a Photo"
        self.loc.pt_info_post_contents = u"Post Contents"
        self.loc.pt_info_new_post = u"New Post"
        self.loc.pt_info_edit_post = u"Edit Post"
        self.loc.pt_info_no_pub = u"Yes"
        self.loc.pt_info_draft = u"No (draft)"
        self.loc.pt_info_no_imgs_sel = u"No images selected."
        self.loc.pt_info_downld_img = u"Downloading %s"
        self.loc.pt_info_alrd_pub = u"Post already published."

        # Posts error messages
        self.loc.pt_err_cant_del_pt = u"Impossible to delete post."
        self.loc.pt_err_cant_start_viewf = u"Could not start the view finder."
        self.loc.pt_err_cant_stop_viewf = u"Could not stop the view finder."
        self.loc.pt_err_cant_take_pic = u"Could not take any photo."
        self.loc.pt_err_cant_gen_prvw = u"Could not generate preview file."
        self.loc.pt_err_cant_prvw = u"Impossible to preview."
        self.loc.pt_err_cant_open = u"Impossible to open %s"
        self.loc.pt_err_cant_downld = u"Impossible to download %s"
        self.loc.pt_err_unknown_ext = u"Unkown externsion for %s"
        
        # Posts popup menu
        self.loc.pt_pmenu_posts = u"Posts:"
        self.loc.pt_pmenu_del_post = u"Delete post ?"
        self.loc.pt_pmenu_res = u"Resolution ?"
        self.loc.pt_pmenu_flash = u"Flash ?"
        self.loc.pt_pmenu_img_src = u"Image from:"
        self.loc.pt_pmenu_img_url = u"Image URL:"
        self.loc.pt_pmenu_link_url = u"Link URL:"
        self.loc.pt_pmenu_send_post = u"Send post ?"
        self.loc.pt_pmenu_post_title = u"Post title:"
        self.loc.pt_pmenu_images = u"Images"
        self.loc.pt_pmenu_updt_post = u"Update post ?"

        # Settings info
        self.loc.st_info_blog_set = u"Blog settings"
        self.loc.st_info_proxy_set = u"Proxy settings"
        
        # Settings error
        self.loc.st_err_no_access_point = u"Could't find any access point."
        self.loc.st_err_one_ap_req = u"At least one access point is required."
        
        # Settings query
        self.loc.st_query_access_points = u"Access points:"
        self.loc.st_query_proxy_add = u"Proxy address:"
        self.loc.st_query_proxy_prt = u"Proxy port:"
        self.loc.st_query_proxy_usr = u"Proxy username:"
        self.loc.st_query_proxy_pwd = u"Proxy password:"
        
        # Settings menu
        self.loc.st_menu_canc = u"Cancel"
        self.loc.st_menu_blog = u"Blog"
        self.loc.st_menu_proxy = u"Proxy"
        self.loc.st_menu_access_point = u"Access Point"
        self.loc.st_menu_lang = u"Language"
        self.loc.st_menu_blog_url = u"Blog URL:"
        self.loc.st_menu_blog_usr = u"Username:"
        self.loc.st_menu_blog_pwd = u"Password:"
        self.loc.st_menu_blog_npt = u"Number of posts:"
        self.loc.st_menu_blog_cpp = u"Number of comments per post:"
        self.loc.st_menu_blog_eml = u"Email (for comments):"
        self.loc.st_menu_blog_rnm = u"Real name (for comments):"
        self.loc.st_menu_proxy_ena = u"Enabled"
        self.loc.st_menu_proxy_add = u"Address"
        self.loc.st_menu_proxy_prt = u"Port"
        self.loc.st_menu_proxy_usr = u"Username"
        self.loc.st_menu_proxy_pwd = u"Password"
        self.loc.st_menu_proxy_on = u"Enabled"
        self.loc.st_menu_proxy_off = u"Disabled"
        # languages support
        self.loc.st_menu_en_us = u"English (USA)"
        self.loc.st_menu_pt_br = u"Portuguese"
        
        # Setting popup menu
        self.loc.st_pmenu_lang = u"Language:"

        # Window
        self.loc.wi_info_exit = u"Exit"

        # Wpwrapper error
        self.loc.wp_err_cant_del_cat = u"Impossible to delete category %s."
        self.loc.wp_err_cant_create_cat = u"Impossible to create category %s."
        self.loc.wp_err_cant_downl_cat =u"Impossible to retrieve the categories list."
        self.loc.wp_err_cant_updt_post = u"Impossible to update posts."
        self.loc.wp_err_cant_downl_post = u"Impossible to download the post. Try again."
        self.loc.wp_err_cant_upld_img = u"Impossible to upload %s. Try again."
        self.loc.wp_err_cant_pub_post = u"Impossible to publish the post. Try again."
        self.loc.wp_err_cant_updt_post_list = u"Impossible to update post title list. Try again."
        self.loc.wp_err_cant_updt_the_post = u"Impossible to update the post. Try again."
        self.loc.wp_err_cant_downl_cmt = u"Impossible to download comments. Try again."
        self.loc.wp_err_cant_updt_cmt = u"Impossible to update the comment. Try again."
        self.loc.wp_err_cant_updt_cmt_list = u"Impossible to update the comment list. Try again."
        self.loc.wp_err_cant_pub_cmt = u"Impossible to publish the comment. Try again."
        self.loc.wp_err_cant_appr_cmt = u"Impossible to approve the comment. Try again."
        self.loc.wp_err_cant_del_cmt = u"Impossible to delete the comment. Try again."

        # Wpwrapper info
        self.loc.wp_info_cat_del = u"Category %s deleted."
        self.loc.wp_info_upld_img = u"Uploading %s..."
        self.loc.wp_info_upld_post_cont = u"Uploading post contents..."
        self.loc.wp_info_updt_post_list = u"Updating post list..."
        self.loc.wp_info_cmt_approved = u"Comment approved."
        self.loc.wp_info_cmt_del = u"Comment deleted."
        
        # Wpwrapper list
        self.loc.wp_list_uncategorized = u"Uncategorized"
        
class Locale(Default):
    "Multiple language support class"
    
    LOC_MODULE = "wmlocale_%s"
    
    def __init__(self,lang = ""):
        "Load all locale strings for one specific language or default if empty"        
        self.set_locale(lang)

    def set_locale(self,lang = ""):
        "Load all locale strings for one specific language or default if empty"
        Default.__init__(self)

        try:
            lang_mod = __import__( self.LOC_MODULE % ( lang ) )
        except ImportError:
            pass
        else:
            self.merge_locale(lang_mod)
        
    def merge_locale(self, lang_mod):
        "Merge new location string into default locale"

        # replace existing strings and keep old ones
        # if it is missing in the locale module
        for k,v in self.loc.__dict__.iteritems():
            if hasattr(lang_mod,k):
                nv = lang_mod.__getattribute__(k)
                self.loc.__setattr__(k,nv)  

LABELS = Locale()
