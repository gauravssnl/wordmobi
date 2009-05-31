# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
# License: GPL3

import urllib
from appuifw import *
import e32

class WPStats(object):
    """ This classe uses urllib for accessing wordpress blog statistics.
        Only blogs hosted at wordpress.com may be used.
    """

    STAT_URL = "http://stats.wordpress.com/csv.php?"
    
    def __init__(self,api_key,blog_uri,blog_id=0,max_days=30):
        """ Init WPStats parmeters.

            Please use:
                api_key: copy it from http://yourblogname.wordpress.com/wp-admin/profile.php
                blog_uri: your blog uri (http://yourblogname.wordpress.com)
                max_days: all accesses will provided statistics for the last max_days
        """
        self.api_key = api_key
        self.blog_uri = blog_uri
        self.blog_id = blog_id
        self.max_days = max_days

    def __request_stats(self,custom_params):
        """ Common request function. Additional parameters may be
            encoded for GET using custom_params dictionary
        """
        params = {"api_key":self.api_key,
                  "blog_id":self.blog_id,
                  "blog_uri":self.blog_uri,
                  "format":"cvs",
                  "days":self.max_days}
        params.update(custom_params) # add custom_params values to params

        try:
            f = urllib.urlopen(self.STAT_URL + urllib.urlencode(params))
        except Exception, e:
            raise e
        
        data = []        
        rsp = f.read()
        if rsp:
            # this split may fail for post title with "\n" on it - improve it
            data = rsp.split("\n")[1:-1] # discard column names and last empty element

        return data

    def get_post_views(self,post_id = 0):
        """ Get the number of views for a given post id or
            number of views for all posts (post id = 0)
            
            Response is an array of tuples like below:
            [(date,post_id,views),date,post_id,views),...]
        """
        params = {"table":"postviews"}
        if post_id:
            params['post_id'] = post_id
        data = self.__request_stats(params)
        res = []
        for d in data:
            # this split may fail for post title with "," on it
            row = d.split(",")
            res.append((row[0],row[1],row[-1]))
        return res

    def get_blog_views(self):
        """ Get the number of views

            Response format is an array of tuples like below:
            [(date,views),(date,views),...]
        """
        params = {"table":"view"}
        data = self.__request_stats(params)
        res = []
        for d in data:
            res.append(tuple(d.split(",")))
        return res
   
class WPStatClient(object):
    """ Get statistics from wordpress
    """
    def __init__(self):       
        self.lock = e32.Ao_lock()
        app.title = u"WP Stats demo"
        app.menu = [(u"Get blog views", self.blog_views),
                    (u"Get post views", self.post_views),
                    (u"About", self.about),
                    (u"Exit", self.close_app)]
        self.body = Listbox([(u"Please, update statistics",u"")])
        app.body = self.body
        app.screen = "normal"        
        self.wpstats = WPStats("api_key_here","http://blog_name_here.wordpress.com")
        self.lock.wait()

    def blog_views(self):
        try:
            bv = self.wpstats.get_blog_views()
        except:
            note(u"Impossible to get stats","error")
        else:
            if bv:
                items = []
                for stat in bv:
                    items.append((unicode(stat[0]),
                                  u"Views:" + unicode(stat[1])))
                self.body.set_list(items)
            else:
                self.body.set_list([(u"",u"")])

    def post_views(self):
        try:
            pv = self.wpstats.get_post_views()
        except:
            note(u"Impossible to get stats","error")
        else:
            if pv:
                items = []
                for stat in pv:
                    items.append((unicode(stat[0]),
                                  u"PostID:"+unicode(stat[1]) + u"  Views:"+unicode(stat[2])))
                self.body.set_list(items)
            else:
                self.body.set_list([(u"",u"")])

    def about(self):
        note(u"WP stats demo by Marcelo Barros (marcelobarrosalmeida@gmail.com)","info")
        
    def close_app(self):
        self.lock.signal()
        app.set_exit()

if __name__ == "__main__":
    WPStatClient()
    



