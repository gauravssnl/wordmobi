# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com

import simplejson as json
import urllib

class QikApi(object):
    """ Simple class for Qik videos proxy support
    """
    def __init__(self, api_key, qik_usr):
        """ Create a new Qik API instance with given API key and user name
        """
        self.qik_url = 'http://engine.qik.com/api/jsonrpc?apikey=' + api_key
        self.qik_usr = qik_usr
        self.qik_id = -1

    def __urlopener(self):
        """ Return an urlopener with Qik required headers already set
        """
        urlopener = urllib.URLopener()
        urlopener.addheaders = [('Host','engine.qik.com'),
                                ('Content-Type','application/json; charset=UTF-8')]
        return urlopener

    def __open(self,url,params=""):
        """ Open a given URL using GET or POST and Qik headers
        """
        if params:
            f = self.__urlopener().open(url,params) #post
        else:
            f = self.__urlopener().open(url) #get
            
        return f
    
    def __qik_request(self,data):
        """ Qik request. Encode data in json format, do the request and
            decode json response
        """
        data = json.dumps(data)
        f = self.__open(self.qik_url,data)
        res = json.loads(f.read())[0]
        return res

    def __check_id(self,qik_id):
        """ Check if user ID was retrieved or not. If not, download it
        """
        if qik_id == -1:
            if self.qik_id == -1:
                self.qik_id = self.get_user_public_profile()[u'id']
            qik_id = self.qik_id
        return qik_id
    
    def get_public_user_streams(self,usr=''):
        """ Return all public stream for a given user
            (or for the current user, if it not provided)
        """
        if not usr:
            usr = self.qik_usr
        data = {'method': 'qik.stream.public_user_streams','params': [usr]}
        return self.__qik_request(data)

    def get_user_public_profile(self,usr=''):
        """ Return public profile for a given user
            (or for the current user, if it not provided)
        """        
        if not usr:
            usr = self.qik_usr
        data = {'method': 'qik.user.public_profile','params': [usr]}
        return self.__qik_request(data)
    
    def get_user_public_detailed_profile(self,usr=''):
        """ Return detailed public profile for a given user
            (or for the current user, if it not provided)
        """          
        if not usr:
            usr = self.qik_usr
        data = {'method': 'qik.user.public_detailed_profile','params': [usr]}
        return self.__qik_request(data)     

    def get_user_followers(self,qik_id=-1):
        """ Return the list of followers for a given user
            (or for the current user, if it not provided)
        """          
        qik_id = self.__check_id(qik_id)
        data = {'method': 'qik.user.followers','params': [qik_id]}
        return self.__qik_request(data)

    def get_user_following(self,qik_id=-1):
        """ Return the list of following for a given user
            (or for the current user, if it not provided)
        """         
        qik_id = self.__check_id(qik_id)
        data = {'method': 'qik.user.following','params': [qik_id]}
        return self.__qik_request(data)

    def get_public_stream_info(self,vid_id):
        """ Get detailed information about some public video
        """
        data = {'method': 'qik.stream.public_info','params': [vid_id]}
        return self.__qik_request(data)
