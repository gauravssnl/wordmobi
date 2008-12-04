import beautifulsoup as bs
import os
import urllib

proxy = "http://barros:22janKKT@192.168.1.40:8080"



def check_update(proxy,curr_version):

    url = 'http://code.google.com/p/wordmobi/wiki/LatestVersion'
    os.environ["http_proxy"] = proxy
    
    html = urllib.urlopen( url ).read()
    soup = bs.BeautifulSoup( html )

    version = ""
    location = ""

    upd_info = soup.findAll('a')
    for info in upd_info:
        if info.has_key('href'):
            contents = info.contents[0]
            print contents
            if contents == u"latest_wordmobi_version":
                version = info['href'].replace('http://','').encode('utf-8')
            elif contents == u"wordmobi_sis_url":
                location = info['href'].encode('utf-8')

    curr_digts = [ int(s) for s in curr_version.split(".") ]
    curr = sum(map( lambda x,y: x*y, curr_digts, [100, 10, 1]))

    latest_digts = [ int(s) for s in version.split(".") ]
    latest = sum(map( lambda x,y: x*y, latest_digts, [100, 10, 1]))

    print curr, latest
    if latest > curr:
        print "update!"
    
        print "Location = %s" % location
        print "Version = %s" % version

        if location and version:
            local_file = "wordmobi-" + version + ".sis"
            urllib.urlretrieve( location , local_file )



check_update(proxy,"0.2.7")
