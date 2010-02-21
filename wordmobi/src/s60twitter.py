# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com

# TODO use just UrllibProxy, removing all no necessary stuff

import base64
import urllib
from urllib import unquote, splittype, splithost
import simplejson as json
import mktimefix as time

__all__ = [ "TwitterApi" ]

class _FancyURLopener(urllib.FancyURLopener):
    """ This class handles basic auth, providing user and password
        when required by twitter
    """
    def __init__(self, usr, pwd, prx={}):
        """ Set default values for local proxy (if any)
            and set user/password for twitter
        """
        urllib.FancyURLopener.__init__(self,prx)
        self.usr = usr
        self.pwd = pwd
        
    def prompt_user_passwd(self, host, realm):
        """ Basic auth callback
        """
        return (self.usr,self.pwd)
    
class TwitterApi(object):
    """ Simple class for twitter update with proxy support
    """
    def __init__(self, tw_usr, tw_pwd, proxy=""):
        """ Set default values for local proxy (if any)
            and set user/password for twitter
        """
        self.proxyurl = proxy
        self.user_agent = "urllib/1.0 (urllib)"
        self.tw_usr, self.tw_pwd = tw_usr, tw_pwd
        self._prepare_urlopener()

    def _prepare_urlopener(self):
        """ Update twitter status
        # http://code.activestate.com/recipes/523016/
        """
        if self.proxyurl:
            XXX, r_type = splittype(self.proxyurl)
            phost, XXX = splithost(r_type)
            puser_pass = None
            if '@' in phost:
                user_pass, phost = phost.split('@', 1)
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    puser_pass = base64.encodestring('%s:%s' %
                                                     (unquote(user),
                                                      unquote(password))).strip()            
            self.urlopener_proxy = {'http':'http://%s'%phost}
            if not puser_pass:
                self.headers = [('User-agent', self.user_agent)]
            else:
                self.headers = [('User-agent', self.user_agent),
                                ('Proxy-authorization', 'Basic ' + puser_pass) ]
        else:
            self.urlopener_proxy = {}
            self.headers = []

    def _get_urlopener(self):
        """ Return an urlopener with authentication headers and proxy already set
        """
        urlopener = _FancyURLopener(self.tw_usr, self.tw_pwd, self.urlopener_proxy)
        urlopener.addheaders = self.headers
        return urlopener
        
    def update(self, status, in_reply_to=""):
        """ Update twitter with new status message
        """
        params = urllib.urlencode({"status":status,"in_reply_to_status_id":in_reply_to})
        f = self._get_urlopener().open("http://twitter.com/statuses/update.json", params)
        d = f.read()
        return self.json_read(d)

    def new_direct_message(self,text,user):
        """ Send a direct message (text) to user
        """
        params = urllib.urlencode({"text":text,"user":user})
        f = self._get_urlopener().open("http://twitter.com/direct_messages/new.json", params)
        d = f.read()
        return self.json_read(d)
    
    def _strptime(self,ts):
        months = [u'Jan',u'Feb',u'Mar',u'Apr',u'May',u'Jun',
                  u'Jul',u'Aug',u'Sep',u'Oct',u'Nov',u'Dec']    
        (dw,mo,day,tm,sec,yr) = ts.split()
        (h,m,s) = tm.split(u":")
        mo = months.index(mo) + 1
        return (int(yr),mo,int(day),int(h),int(m),int(s),0,0,0)

    def human_msg_age(self,ts):
        """ Human message reporting message age. ts is the time stamp provided
            by twitter (string).
            See function GetRelativeCreatedAt()
            http://code.google.com/p/python-twitter/source/browse/trunk/twitter.py
        """
        fudge = 1.25
        ma = time.mktime(self._strptime(ts))
        delta  = int(time.mktime(time.gmtime())) - int(ma)

        if delta < (1 * fudge):
          return u'~1s ago'
        elif delta < (60 * (1/fudge)):
          return u'~%ds ago' % (delta)
        elif delta < (60 * fudge):
          return u'~1m ago'
        elif delta < (60 * 60 * (1/fudge)):
          return u'~%dm ago' % (delta / 60)
        elif delta < (60 * 60 * fudge):
          return u'~1h ago'
        elif delta < (60 * 60 * 24 * (1/fudge)):
          return u'~%dh ago' % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge):
          return u'~1d ago'
        else:
          return u'~%dd ago' % (delta / (60 * 60 * 24))


    def get_friends_timeline(self,page=1,count=20):
        """ Return friends timeline for current user and his friends
        """
        params = urllib.urlencode({"page":page,"count":count})
        url = "http://twitter.com/statuses/friends_timeline.json?" + params
        f = self._get_urlopener().open(url)
        d = f.read()
        return self.json_read(d)
    
    def get_user_timeline(self,page=1,count=20):
        """ Return friends timeline for current user
        """
        params = urllib.urlencode({"page":page,"count":count})
        url = "http://twitter.com/statuses/friends_timeline.json?" + params
        f = self._get_urlopener().open(url)
        d = f.read()
        return self.json_read(d)

    def destroy(self,udpt_id):
        """ Destroy the status specified by udpt_id
        """
        url = 'http://twitter.com/statuses/destroy/%s.json' % udpt_id
        f = self._get_urlopener().open(url,"")
        d = f.read()
        return self.json_read(d)
    
    def json_read(self,msg):
        """ Converts a json response from twitter in a python object
        """
        return json.loads(msg)

    def tinyfy_url(self,longurl):
        """ Creates a tiny url using http://is.gd/api_info.php service
        """
        params = urllib.urlencode({"longurl":longurl})
        url = 'http://is.gd/api.php?' + params
        f = self._get_urlopener().open(url)
        rsp = "".join(f.readlines())
        return rsp
    


    
