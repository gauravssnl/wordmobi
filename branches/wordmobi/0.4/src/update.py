from beautifulsoup import BeautifulSoup
import urllib, time, os

DEFDIR = ""

def upgrade_wordmobi():
    url = "http://code.google.com/p/wordmobi/wiki/LatestVersion"
    local_file = "web_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
    local_file = os.path.join(DEFDIR, "/tmp", local_file)
    #t = app.title
    #BaseTabWin.disable_tabs()
    try:
        urllib.urlretrieve( url, local_file )
    except:
        print "erro 1"
        #note(u"Impossible to download %s" % url,"error")

    html = open(local_file).read()
    soup = BeautifulSoup( html )
    addrs = soup.findAll('a')
    version = ""
    file_url = ""
    for addr in addrs:
        print addr.contents[0]
        if addr.contents[0] == "latest_wordmobi_version":
            version = addr["href"]
        elif addr.contents[0] == "wordmobi_sis_url":
            file_url = addr["href"]
    if version and file_url:
        print file_url
        local_file = file_url[file_url.rfind("/")+1:]
        print local_file
        local_file = os.path.join(DEFDIR, "/tmp", local_file)
        try:
            urllib.urlretrieve( file_url, local_file )
        except:
            print "erro 2"
            #note(u"Impossible to download %s" % url,"error")
        
#    app.title = t
 #   BaseTabWin.restore_tabs()
    
upgrade_wordmobi()
