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
