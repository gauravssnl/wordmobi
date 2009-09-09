# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
import base64
import urllib
from urllib import unquote, splittype, splithost

__all__ = [ "UrllibProxy" ]

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
    
class UrllibProxy(object):
    """ Simple class for fetching URLs via urllib.
        It adds proxy support and http basic authentication.
    """
    def __init__(self, proxy="", usr="", pwd=""):
        """ Access a given url using proxy and possible http basic auth
        """
        self.proxy = proxy
        self.url = ""
        self.usr, self.pwd = usr, pwd
        self.user_agent = "urllib/1.0 (urllib)"
        self._prepare_urlopener()

    def _prepare_urlopener(self):
        """ Update twitter status
        # http://code.activestate.com/recipes/523016/
        """
        if self.proxy:
            XXX, r_type = splittype(self.proxy)
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

    def urlopener(self):
        """ Return an urlopener with authentication headers and proxy already set
        """
        urlopener = _FancyURLopener(self.usr, self.pwd, self.urlopener_proxy)
        urlopener.addheaders = self.headers
        return urlopener

    def open(self,url,params=""):
        self.url = url
        if params:
            f = self.urlopener().open(self.url,params) #post
        else:
            f = self.urlopener().open(self.url) #get
            
        return f

    def urlretrieve(self, url, filename=None):
        if not filename:
            filename = url[url.rfind("/") + 1:]
        f = open(filename,"wb")    
        f.write(self.open(url).read())
        
        
    
        
