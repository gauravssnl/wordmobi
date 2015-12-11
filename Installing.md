# Read this page carefully, the whole page #

  * Use [issue tracker](http://code.google.com/p/wordmobi/issues/list) to report problems instead commenting this page.
  * Send me an email instead commenting this page ( marcelobarrosalmeida (_at_) gmail.com  ).
  * Comment this page if you really think that it is necessary (page with errors, tips for installing, problems not covered but solved by you and so on).

# Installation #

## Certification issues ##

You must <font color='blue'><b>enable the installation of any application in your mobile phone, not only the certificated ones</b></font>. In Settings->Applications->App. Manager allow all applications and disable certification checks. If you receive messages related to "old certificates", just change your phone date to nearly one year ago and try to install Wordmobi again.

## Python for S60 installation ##

Install [Python 2.0 runtime](http://milkshake.googlecode.com/files/Python_2.0.0.sis) and [pips](http://milkshake.googlecode.com/files/pips.sis).

If you are using old Wordmobi 0.9.3, you need install [Python 1.9.6 runtime](http://wordmobi.googlecode.com/files/Python_1.9.6.sis). In this case, some phones like N79 may require an special PyS60 version, called [Python\_1.9.6\_fixed.sis](https://garage.maemo.org/frs/download.php/6359/Python_1.9.6_fixed.sis) (thanks to benjaminroesneremail@Jul 27, 2009).

## Wordmobi installation ##

Install [Wordmobi 0.9.5](http://wordmobi.googlecode.com/files/Wordmobi-0.9.5.sis).

<font color='blue'><b>Wordmobi and Python runtime must be installed in the same location</b></font>, phone memory or memory card. Python runtime does not support applications in different locations.

# Setup #

## Wordmobi setup ##

Before using wordmobi, please setup your blog account, user details, proxy (if any) and access point. Proxy is supported, even if using  authentication. If your access point is not listed, please, save it to your connections before starting wordmobi.

<font color='blue'><b>Usernames are case sensitive for wordpress</b></font>, so take care when typing your username. Check if all fields does not have any trailer space.

Wordmobi was designed to support any domain running wordpress with compatible XMLRPC API. <font color='blue'><b>Just set your blog address</b></font> (for instance, http://www.mydomain.com or http://myblog.wordpress.com). If you have your blog running inside some subdirectory, like /my/blog, use http://www.mydomain.com/my/blog. <font color='blue'><b>Do not put any trailing slash and do not put xmlrpc.php at the end</b></font> (they are automatically removed and just added when accessing your blog).

However, if your blog has a customized URL for XMLRPC API (not ending with xmlrpc.php), this URL will not be replaced. Just fill the blog address with you customized URL, including the php file name.

## Wordpress setup ##

<font color='blue'><b>It is necessary to activate xmlrpc support in wordpress for people running blogs in their own domains</b></font> (blogs hosted in Wordpress.com have this option enabled per default). Check the following link to enable it (replace it using your blog URL):

http://your_blog_url/wp-admin/options-writing.php

See [this link](http://coolwebdeveloper.com/2008/12/writing-your-wordpress-blog-articles-remotely-using-xml-rpc-using-windows-live-writer-with-your-wordpress-blog/) and [this](http://www.wpnotifier.com/enable_xmlrpc.php).

Comments will work only with Wordpress [2.6.2](http://comox.textdrive.com/pipermail/wp-xmlrpc/2008-October/000277.html) or newer.

## Blog statistics ##

If you want to use blog view statistics, pay attention in the following points:
  * For people running blogs in wordpress.com, just take note of your [API key](http://faq.wordpress.com/2005/10/19/api-key/) and setup your account with it.
  * For blogs not hosted by wordpress, please read [this page](http://en.wordpress.com/features/stats/) for tips about configuring the required plugin. Feedback is welcome since I do not have blogs outside wordpress.

If you are not receiving the blog view statistics, please do the following:
  * Put the following URL in your browser <font color='blue'><b><a href='http://stats.wordpress.com/csv.php?api_key={your_api}&blog_uri={your_blog_uri}&blog_id=0&days=365&limit=-1'>http://stats.wordpress.com/csv.php?api_key={your_api}&amp;blog_uri={your_blog_uri}&amp;blog_id=0&amp;days=365&amp;limit=-1</a></b></font>  replacing {your\_api} for you API key and {your\_blog\_uri} for your blog URL (the same string you put at account setup dialog, like http://yourblog.wordpress.com). Remove brackets for both fields.
  * Check if you are receiving a valid response with statistics or just a help page.

## Wordmobi directories ##

Wordmobi saves all relevant data in the drive you have chosen, under directory {drive}:\data\python\wordmobidir. The following directories are used:

  * {drive}:\data\python\wordmobidir => wordmobi python files and configuration files
  * {drive}:\data\python\wordmobidir\cache => temporary downloads and temporary htmls files used during preview. Its contents is cleared when wordmobi is closed.
  * {drive}:\data\python\wordmobidir\images => snapshots taken
  * {drive}:\data\python\wordmobidir\loc => locales
  * {drive}:\data\python\wordmobidir\res => resource images

# Known problems #

  * Some devices does not support media selection using thumbnails (Wordmobi-{version}.sis) and <font color='blue'><b>Wordmobi closes unexpectedly</b></font>. In this case try to use the version without thumbnails (<font color='blue'><b>Wordmobi-{version}-nomgfetch.sis</b></font>). This error was reported [here](http://code.google.com/p/wordmobi/issues/detail?id=69)