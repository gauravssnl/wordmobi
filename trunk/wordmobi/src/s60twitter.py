# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com

# TODO use just UrllibProxy, removing all no necessary stuff

import base64
import urllib
from urllib import unquote, splittype, splithost
import simplejson as json

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
        
    def update(self, status):
        """ Update twitter with new status message
        """
        status = 'status=' + status
        f = self._get_urlopener().open("http://twitter.com/statuses/update.json", status)
        d = f.readlines()[0]
        return self.json_read(d)
    
    def get_friends_timeline(self,page=1,count=20):
        """ Return friends timeline for current user
        """
        url = 'http://twitter.com/statuses/friends_timeline.json?page=%d&count=%d' % (page,count)
        f = self._get_urlopener().open(url)
        d = f.readlines()[0]
        return self.json_read(d)
    
    def get_user_timeline(self,page=1,count=20):
        """ Return friends timeline for current user
        """
        url = 'http://twitter.com/statuses/user_timeline.json?page=%d&count=%d' % (page,count)
        f = self._get_urlopener().open(url)
        d = f.readlines()[0]
        return self.json_read(d)

    def json_read(self,msg):
        """ Converts a json response from twitter in a python object
        """
        return json.loads(msg)
    
    def dirty_tinyfy_url(self,page):
        """ Creates a tiny url using http://tinyurl.com/ service
        """
        params = "url=%s" % page
        url = 'http://tinyurl.com/create.php'
        f = self._get_urlopener().open(url,params)
        rsp = "".join(f.readlines())
        b = rsp.find('" target="_blank"')
        a = rsp.rfind('"',0,b) + 1
        return rsp[a:b]

    def tinyfy_url(self,page):
        """ Creates a tiny url using http://is.gd/api_info.php service
        """
        url = 'http://is.gd/api.php?longurl=%s' % page
        f = self._get_urlopener().open(url)
        rsp = "".join(f.readlines())
        return rsp
    


    
