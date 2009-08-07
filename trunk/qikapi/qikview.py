# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
# License: GPL3

import sys
sys.path.append('e:\\Python')

import window
from appuifw import *
from qikapi import QikApi
import time

API_KEY = 'YOUR_API_KEY'

QIK_TEMPLATE = u"""
<html><head><meta http-equiv="Content-Type" content="application/vnd.wap.xhtml+xml; charset=utf-8" /><title>__TITLE__</title></head><body>
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="220" height="185" id="player" align="middle">
<param name="movie" value="http://qik.com/swfs/qik_player_lite.swf?file=http://qik.com/flv/__FILENAME__.flv&amp;thumbnail=http://qik.com/redir/__FILENAME__.jpg&amp;size=false&amp;aplay=true&amp;autorew=false&amp;layout=small&amp;title=__TITLE__"/>
<param name="menu" value="false" />
<param name="quality" value="high" />
<param name="bgcolor" value="#999999" />
<embed src="http://qik.com/swfs/qik_player_lite.swf?file=http://qik.com/flv/__FILENAME__.flv&amp;thumbnail=http://qik.com/redir/__FILENAME__.jpg&amp;size=false&amp;aplay=true&amp;autorew=false&amp;layout=small&amp;title=__TITLE__" menu="false" quality="high" bgcolor="#999999" width="220" height="185" name="player" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"/>
</object></body></html>
""".encode('utf-8')

class QikView(window.Application):
    def __init__(self):
        self.qik_usr = u""
        self.qik_api = None
        self.data = {'profile':[], 'streams':[], 'followers':[], 'following':[]}
        # menus
        streams_menu = [(u"Show stream",self.show_video)]
        common_menu = [(u"Update",self.update),
                       (u"Setup",self.setup),
                       (u"About",self.about)]
        # bodies
        self.streams = Listbox([(u"Please, setup and update",u"")],self.show_video)
        self.following = Listbox([(u"Please, setup and update",u"")])
        self.followers = Listbox([(u"Please, setup and update",u"")])

        window.Application.__init__(self,
                             u"Qik View",
                             [(u"Streams",self.streams,streams_menu),
                              (u"Following",self.following,[]),
                              (u"Followers",self.followers,[])],
                             common_menu)

    def update(self):
        if not self.qik_usr or not self.qik_api:
            note(u"Please, setup the Qik user",u"error")
        else:
            self.lock_ui()
            try:
                self.set_title(u"Updating profile...")
                self.data['profile'] = self.qik_api.get_user_public_profile()
                self.set_title(u"Updating streams...")
                self.data['streams'] = self.qik_api.get_public_user_streams()
                self.set_title(u"Updating followers...")
                self.data['followers'] = self.qik_api.get_user_followers()
                self.set_title(u"Updating following...")
                self.data['following'] = self.qik_api.get_user_following()
            except:
                note(u"Network error. Please, try again","error")
            else:
                self.update_bodies()
            self.set_title(u"Qik View")
            self.unlock_ui()
            self.refresh()

    def update_bodies(self):
        streams = []
        followers = []
        following = []
        
        for s in self.data['streams']:
            h1 = s['title'] + (u" (%ds)" % s['duration'])
            h2 = s['created_at']
            streams.append((h1,h2))

        for f in self.data['followers']:
            followers.append((f[u'username'],f[u'full_name']))
            
        for f in self.data['following']:
            following.append((f[u'username'],f[u'full_name']))

        if streams:
            self.streams.set_list(streams)
        else:
            self.streams.set_list([(u"No streams available",u"")])

        if followers:
            self.followers.set_list(followers)
        else:
            self.followers.set_list([(u"No followers available",u"")])

        if following:
            self.following.set_list(following)
        else:
            self.following.set_list([(u"No following available",u"")])            
        
    def setup(self):
        usr = query(u"Qik user:","text",self.qik_usr)
        if usr is not None:
            self.qik_usr = usr
            self.qik_api = QikApi(API_KEY,self.qik_usr)
            
    def show_video(self):
        if self.data['streams']:
            # retrieve information about video
            idx = self.streams.current()
            if not self.data['streams'][idx].has_key('stream_info'):
                vid = self.data['streams'][idx][u'id']
                self.lock_ui(u"Downloading stream info...")
                try:
                    self.data['streams'][idx]['stream_info'] = self.qik_api.get_public_stream_info(vid)
                except:
                    note(u"Network error. Please, try again","error")
                    ret = True
                else:
                    ret = False
                self.set_title(u"Qik View")
                self.unlock_ui()
                self.refresh()
                if ret:
                    return
            tit = self.data['streams'][idx]['stream_info'][u'title'].encode('utf-8')
            fn = self.data['streams'][idx]['stream_info'][u'filename'].encode('utf-8')
            html_code = QIK_TEMPLATE.replace('__FILENAME__',fn).replace('__TITLE__',tit)
            html_file = "html_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".html"
            try:
                fp = open(html_file,"wt")
                fp.write(html_code)
                fp.close()
            except:
                note(u"Could not create HTML file","error")
                return
            
            viewer = Content_handler(self.refresh)
            try:
                viewer.open(html_file)
            except:
                note(u"Can not open browser","error")

    def about(self):
        note(u"Qik API for PyS60\nby marcelobarrosalmeida@gmail.com",u"info")

if __name__ == "__main__":
    app = QikView()
    app.run()
