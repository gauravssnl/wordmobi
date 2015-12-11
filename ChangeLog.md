# Change log #

# 0.9.5 - 2011/05/29 #
  * Use Python for S60 2.0
  * Added support for Indonesian (thanks to Nikko Haendratnio)

# 0.9.4 - 2010/02/21 #
  * Use Python for S60 2.0
  * No new features or bug fixed

# 0.9.3 - 2009/09/10 #
  * Use Python for S60 1.9.6
  * Fixed issues [62](http://code.google.com/p/wordmobi/issues/detail?id=62) and [63](http://code.google.com/p/wordmobi/issues/detail?id=63)

# 0.9.2 - 2009/09/09 #
  * Standard S60 media gallery selection using pymgfetch
  * Localization for statistics dialog
  * Russian support
  * Password changes will not remove local persistence anymore
  * Improve "take picture" with white balance, all image modes, flash modes and exposure modes. A bug in Pys60 is not allowing full screen preview of images.
  * Adding link to the full image when it is scaled

# 0.9.1 - 2009/07/21 #
  * Fixing bug related to "api key missing" in new blog accounts
  * Adding proxy support for wp stats api
  * Not hiding anymore the api key in setup dialog

# 0.9.0 - 2009/07/21 #
  * Support for tag "more"
  * Adding blog view statistics. Persistence missing yet.
  * Returning listbox icons
  * French translation added
  * Support for installation on phone memory or card but python runtime must be installed in the same location
  * Only supporting Python 1.9.x.  Python 1.4.x was deprecated.

# 0.8.1 - 2009/05/25 #
  * Tags support added.
  * Recent comments for all post now are fetched with just one command.
  * HTML tags for H1, H2, H3 and H4 added to post edit dialog.
  * It was necessary to remove listbox icons for a while due to some PyS60 1.9.5 incompatibility. We must have them working again soon.
  * 1.9.5 support added (touch devices like XM 5800 now working)

# 0.8.0 - 2009/05/25 #
  * Same changelog of 0.8.1 but only for Python 1.9.4. No sis generated.

# 0.7.0 - 2009/04/04 #
  * Multi wordpress accounts support
  * new account icon for wordpress
  * realname, blog and email dont need to be filled when answering a comment and they were removed from setting. This is added by WP.
  * image selection now saving last directory
  * persist.py now storing a new key, blog\_list. user, pass, blog, num\_posts and num\_comments are deprecated.
  * For local image selection, it is presented a dialog with a scale factor. This scale factor is calculated to generate an image with width of 480px. User may change it if he wants.
  * post status: [#](#.md) draft and not changed locally (visible only when you download the post contents), [**] published and changed locally, [@] local only
  * s60twitter api updated from iamdoing project, using simplejson
  * New dialog for setting multiple blog accounts
  * New languages: simplified chinese
  * Added proxy support for all operations, like update and image download
  * Readable message error from wordpresslib when it fails
  * Persistence for multiple blogs implemented**

# 0.6.1 - 2009/03/15 #
  * Translations added: Romanian, German, Dutch, Italian.
  * Sorting languages in language selection menu
  * Python 1.9.2 and Python 1.4.5 supported

# 0.6.0 (Python 1.9.2 and Python 1.4.5) - 2009/03/03 #
  * [Issue 29](https://code.google.com/p/wordmobi/issues/detail?id=29) - Things to fix
  * [Issue 18](https://code.google.com/p/wordmobi/issues/detail?id=18) - No categories in new post
  * Adding support for Python 1.9.2
### comments.py ###
  * fixing missing locale for "Approve"
### datetime.py ###
  * Adding support for python 1.9.x (import e32calender as calendar)
### default.py ###
  * Adding support for python 1.9.
> > Due to import problems, all .py files need to use extrasdir
> > (see release info for python 1.9.1)
### persist.py ###
  * removing key "categories" (not in use)
### s60twitter.py ###
  * Replacing s60simplejson by original simplejson ported to s60
> > http://code.google.com/p/wordmobi/source/browse/#svn/trunk/simplejson
### wordmobi.py ###
  * appuifw.app.screen='normal'at beggining was required
  * adding all menu option to app.menu
  * saving at exit
  * update support for py1.9 added
### wmutil.py ###
  * [Issue 30](https://code.google.com/p/wordmobi/issues/detail?id=30) - "Impossible to update posts" with 0.4.4.
> > fixing unicode conversion when argument is already unicode
### wmglobals.py ###
  * creating persist file name
  * updating version info
### settings.py ###
  * btsocket replacing socket (see release info for python 1.9.1)
  * [Issue 26](https://code.google.com/p/wordmobi/issues/detail?id=26) - Remove any slash at the end of blog name automatically
> > http://code.google.com/p/wordmobi/issues/detail?id=26&can=1
  * Adding Turkish translation
  * renaming es\_cl to es only
### categories.py ###
  * Missing self.refresh() after adding a item to categories
### posts.py ###
  * [Issue 28](https://code.google.com/p/wordmobi/issues/detail?id=28) - Camera problem E60 (and possibly other S60v3 without cam)
> > http://code.google.com/p/wordmobi/issues/detail?id=28&can=1
  * Adding support for including youtube links
  * Adding support for saving post locally
  * EditPost now using same close\_app() from NewPost
  * Decoding category names properly when EditPost() is called
  * Allowing draft\publish at any time in EditPost(). Now, a published post
> > may be converted to draft.
  * offline\_publish() meny entry added for publishing offline post
  * smart popup menu (only related options are showed)
  * smart delete option, covering all cases for local, remote and mixed
  * EditPost() using post index instead post entry when called
  * Protecting several function against invalid selection from left key menu
> > contents, send2twitter, comments, delete)
  * refresh() with special symbols for
> > Local post only: [@]
> > Remote post with local modification: [**]
  * Improving merge routine:
> > - local only posts are kept unchanged and listed
> > - modified posts with remote copy overwrites the remote copy.
> > > User must delete the local changes if he wants

> > - post are sorted by creation time
### wpwrapper.py ###
  * including cpickle for persistence
  * adding function for persistence: save(), load(), save\_new\_post(),
> > post\_is\_only\_remote(), post\_is\_only\_local(), post\_is\_remote(),
> > post\_is\_local(), save\_exist\_post(), offline\_publish()
  * creating a dictionary with categories for faster processing in
> > categoryName2Id()
  * added build\_cat\_dict() for rebuilding the category dict
  * improving delete\_category() and fixing a localization bug (LABEL.)
  * update\_posts() renamed to update\_posts\_and\_cats() since both need to be
> > updated. Performing merge operation with local posts.
  * edit\_post() changed for support local posts editing
  * several new delete function for covering all cases.
> > - delete\_post() for deleting local/remote post
> > - delete\_only\_remote\_post()
> > - delete\_only\_local\_post()
  * DateTime() must use GMT for better integration with wordpress.
> > WP must be set properly as well
### locales ###
#### added ####
  * cm\_list\_approve = u"Approve"
  * pt\_menu\_offl\_publ = u"Publish"
  * pt\_list\_save\_it = u"No, but save it"
  * pt\_list\_yes\_rem\_pst = u"Yes, just remote post"
  * pt\_list\_yes\_loc\_ch = u"Yes, just local changes"
  * pt\_list\_yes\_del\_all = u"Yes, delete all"
  * pt\_info\_send\_twt = u"Sending post title to Twitter" #no final period
  * pt\_pmenu\_linkyt\_url = u"Youtube URL:"
  * st\_menu\_tr = u"Turkish"
  * st\_menu\_es = u"Spanish"
#### deleted ####
  * pt\_info\_alrd\_pub = u"Post already published."
  * pt\_info\_send\_twt1 = u"Sending post to Twitter."
  * pt\_info\_send\_twt2 = u"Sending post to Twitter.."
  * pt\_info\_send\_twt3 = u"Sending post to Twitter..."
  * pt\_pmenu\_updt\_post = u"Update post ?"
  * st\_menu\_es\_cl = u"Spanish (Chile)"
#### changed ####
  * pt\_pmenu\_send\_post = u"Publish post ?"
  * pt\_err\_cant\_pst\_cont = u"Impossible to download post contents"**

# 0.5.0 for Python 1.9.1 - 2009/02/19 #

  * Replacing s60simplejson by original simplejson ported to s60
> > http://code.google.com/p/wordmobi/source/browse/#svn/trunk/simplejson
  * Modification for running in Python 1.9.1
    * appuifw.app.screen='normal'at beggining was required
    * new ensymble for 1.9.1
    * btsocket replacing socket (see release info for python 1.9.1)
    * e32calendar replacing calendar (see release info for python 1.9.1)
    * fixing unicode conversion when argument is already unicode
    * increasing application heap for 5MB (original 1MB was not working)
    * due to import problems, all .py files need to use extrasdir (see release info for python 1.9.1)
  * **Upgrade option should not be used in this version**.

# 0.5.0 - 2009/02/09 #

  * Spanish translation added. Thanks to Pablo Poo (Chile).
  * Support for sending post titles to twitter.
  * Fixing issue [27](http://code.google.com/p/wordmobi/issues/detail?id=27)

# 0.4.4 - 2009/02/05 #

  * [Multilingual](http://wiki.forum.nokia.com/index.php/Localization_Example_for_PyS60) support added. At this moment, only English and Portuguese (Brazil) are available. If you want to see your language supported, see TranslateWordMobi.

# 0.4.3 - 2009/01/17 #

  * Fixing issue [23](http://code.google.com/p/wordmobi/issues/detail?id=23) -   	 Impossible to send posts in version 0.4.2

# 0.4.2 - 2009/01/13 #

  * Fixing issue [20](http://code.google.com/p/wordmobi/issues/detail?id=20) - Preview is not working on 0.4.0 .
  * Fixing issue [21](http://code.google.com/p/wordmobi/issues/detail?id=21) -  	 UI is not indicating when the updating finishes.
  * Preview now using the correct encoding for HTML (UTF-8)

# 0.4.0 - 2009/01/11 #

  * Navigation based on left\right keys.
  * New UI, based on list boxes instead tabs.
  * Smarter update routine, only downloading when a new version is available.
  * Comment dialog now showing post title.
  * Icons added to the main list box. More are following in future versions for indicating comment\post status, for instance.
  * (Much) better code organization.
  * Sorry, no tag support yet.
  * Fixing issue [19](http://code.google.com/p/wordmobi/issues/detail?id=19)

# 0.3.5 - 2008/12/16 #

  * Fixing issue [16](http://code.google.com/p/wordmobi/issues/detail?id=16). Categories with accents were blocking wordmobi when uploading post.
  * Fixing issue [15](http://code.google.com/p/wordmobi/issues/detail?id=15). Categories mis-spelled on one menu option (thanks to [captainjim](http://code.google.com/u/captainjim/))

# 0.3.4 - 2008/12/08 #

  * Fixing issue [5](http://code.google.com/p/wordmobi/issues/detail?id=5). Categories with accents were blocking wordmobi during category download.

# 0.3.3 - 2008/12/08 #

  * Adding a note related to proxy authentication before downloading the update (About->Check upgrade). urllib does not support authentication for python 2.2.

# 0.3.2 - 2008/12/08 #

  * Fixing issue [12](http://code.google.com/p/wordmobi/issues/detail?id=12)
  * New versions can be download now using About->Check upgrade. The sis file is stored in e:\wordmobi\updates

# 0.3.0.1 - 2008/12/07 #

  * [Issue 11](http://code.google.com/p/wordmobi/issues/detail?id=11): After second comment update, edit/view comment continues to show contents from first update

# 0.3.0 - 2008/12/06 #

  * New interface based on tabs
  * Support for categories management (delete, new)
  * Support for comments management (approve, delete, edit, new)
  * New internal organization

# 0.2.10 - 2008/12/05 #

  * Fixing issue [9](http://code.google.com/p/wordmobi/issues/detail?id=9). Thanks to [Sebastian Protasiuk](http://code.google.com/u/Sebastian.Protasiuk/) for reporting and debuging.

  * Small problem in proxy setup when user/pass need to be empty. Once you fill theses fields, never you will erase them again. Now, when you press cancel the field is cleared.

# 0.2.9 - 2008/12/04 #

Initial support for comments added to this version. It is possible to approve, delete and edit comments. However, menus and dialogs for comments may change soon. Moreover, more tests need to be done.

If you want to use this version, put additional required information (email, name) inside Setting->blog.

# 0.2.8 #
  * support for later publishing (draft post)
  * [space tag](http://code.google.com/p/wordmobi/issues/detail?id=7) added