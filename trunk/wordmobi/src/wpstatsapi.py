# -*- coding: utf-8 -*-
"""
Marcelo Barros de Almeida
marcelobarrosalmeida (at) gmail.com
License: GPL3

Documentation from http://stats.wordpress.com/csv.php
"""

import urllib
from urllibproxy import UrllibProxy
import datetime

DEBUG = False

__all__ = [ "WPStats","conv2weekly","conv2monthly" ]

class WPStats(object):
    """ This classe uses urllib for accessing wordpress blog statistics.
    """

    STAT_URL = "http://stats.wordpress.com/csv.php?"
    
    def __init__(self,api_key,blog_uri,blog_id=0,max_days=30,end_day="",proxy=""):
        """ Init WPStats parmeters.

            Please use:
                api_key : copy it from http://yourblogname.wordpress.com/wp-admin/profile.php
                blog_uri: your blog uri (http://yourblogname.wordpress.com)
                max_days: all accesses will provided statistics for the last max_days
                end_day : The last day of the desired time frame.
                          Format is 'Y-m-d' (e.g. 2007-05-01) and default is UTC date.
                proxy: Standard proxy string, like http://user:pass@proxy:port
        """
        self.api_key = api_key
        self.blog_uri = blog_uri
        self.blog_id = blog_id
        self.max_days = max_days
        self.end_day = end_day
        self.prx = proxy

    def reconfigure(self,**params):
        """ Reconfigure module parameters using a dictionary
        """
        valid_params = [ "api_key", "blog_uri", "blog_id",
                         "max_days", "end_day", "proxy" ]
        for k in params.keys():
            if hasattr(self,k) and (k in valid_params):
                self.__setattr__(k,params[k])  

    def __split(self,line):
        """ Split a response in CSV format according to WP CSV API.
            Line must be a string and an tuple with all elements is returned
        """
        if line.find('"') == -1:
            # do a fast split aince no special quotes were found
            return tuple(line.split(','))
        # special split, parsing "quote stuffing"
        fields = []
        n = 0
        in_field = False
        field = ''
        while line:
            c1 = line[n:n+1]
            c2 = line[n+1:n+2]
            if not c1:
                fields.append(line)
                break
            if not c2:
                c2 = ''
            if c1 == ',':
                if not in_field:
                    fields.append(line[:n])
                    line = line[n+1:]
                    n = 0
                    in_field = False
                    field = ''
                    continue
                else:
                    field = field + c1
                    n = n + 1
            elif c1 == '"':
                if not in_field:
                     n = n + 1
                     in_field = True
                else:
                    if c2 == '"':
                         field = field + '"'
                         n = n + 2
                    else:
                        in_field = False
                        n = n + 1
            else:
                field = field + c1
                n = n + 1
        
        return tuple(fields)
          
    def __request_stats(self,custom_params):
        """ Request statistics from wordpress, returning a array with all responses
            Add your custom parameters using the custom_params dictionary.
        """
        prx = UrllibProxy(self.prx)
        params = {"api_key":self.api_key,
                  "blog_id":self.blog_id,
                  "blog_uri":self.blog_uri,
                  "format":"cvs",
                  "days":self.max_days,
                  "limit":-1}
        if self.end_day:
            params['end'] = self.end_day
        params.update(custom_params)

        try:
            url = self.STAT_URL + urllib.urlencode(params)
            if DEBUG: print "URL: ", url
            f = prx.open(url)
        except Exception, e:
            raise e
        
        data = []
        rsp = ""
        try:
            rsp = f.read()
        except Exception, e:
            if DEBUG: print "Error reading URL"
        f.close()
        if DEBUG: print "Downloaded %d kbytes" % (len(rsp)/1024)
       
        if rsp:
            if DEBUG: print "Raw data:\n", rsp
            # this split may fail for post title with "\n" on it - improve it
            # discard column names and last empty element
            data = [ self.__split(line) for line in rsp.split('\n') if len(line) > 10 ]

        return data

    def get_blog_views(self):
        """ Get the number of views

            Response format is an array of tuples like below:
            [(date,views),(date,views),...] where date is 'Y-m-d' string
            and views is an integer
        """
        params = {"table":"view"}
        data = self.__request_stats(params)
        data = [ (d[0],int(d[1])) for d in data ]
        return data

    def get_post_views(self,post_id = 0):
        """ Get the number of views for a given post id or
            number of views for all posts (post id = 0)
            
            Response is an array of tuples like below:
            [(date,post_id,post_title,post_permalink,views),
             (date,post_id,post_title,post_permalink,views),...]
        """
        params = {"table":"postviews"}
        if post_id:
            params['post_id'] = post_id
        return self.__request_stats(params)
    
    def get_referrers(self):
        """ Get referrers.

            Response is an array of tuples like below:        
            [(date,referrer,views),(date,referrer,views),...]
        """
        params = {"table":"referrers"}
        return self.__request_stats(params)

    def get_search_terms(self):
        """ Get search terms.

            Response is an array of tuples like below:        
            [(date,searchterm,views),(date,searchterm,views),...]
        """
        params = {"table":"searchterms"}
        return self.__request_stats(params)
    
    def get_clicks(self):
        """ Get link clicks.

            Response is an array of tuples like below:        
            [(date,click,views),(date,click,views),...]
        """
        params = {"table":"clicks"}
        return self.__request_stats(params)

def conv2monthly(stat):
    """ Converts a daily statistics to montly statistics.
        Return a  array of tuples like below:
        [('Y-m',views),('Y-m',views),...]
    """
    monthly = {}
    for s in stat:
        v  = s[1]
        ym = "-".join(s[0].split('-')[:2])
        if not monthly.has_key(ym):
            monthly[ym] = 0
        monthly[ym] = monthly[ym] + v
    monthly = monthly.items()
    monthly.sort()
    return monthly

def conv2weekly(stat):
    """ Converts a daily statistics to weekly statistics
        Return a  array of tuples like below:
        [('Y-week_number',views),('Y-week_number',views),...]
    """
    weekly = {}
    for s in stat:
        v  = s[1]
        (y,m,d) = [ int(x) for x in s[0].split('-') ]
        dt = datetime.date(y,m,d)
        (isoy,isown,isowd) = dt.isocalendar()
        yw = "%d-%02d" % (isoy,isown)
        if not weekly.has_key(yw):
            weekly[yw] = 0
        weekly[yw] = weekly[yw] + v
    weekly = weekly.items()
    weekly.sort()
    return weekly

if __name__ == "__main__":
    api_key = raw_input("Enter your apy_key: ")
    blog_uri = raw_input("Enter your blog address: ")
    wps = WPStats(api_key,blog_uri)
    bv = wps.get_blog_views()
    pv = wps.get_post_views()
    rf = wps.get_referrers()
    st = wps.get_search_terms()
    ck = wps.get_clicks()
    # testing reconfigure
    wps.reconfigure(api_key="",blog_uri="",blog_id=0,max_days=0,end_day="2009-05-06",proxy="")
