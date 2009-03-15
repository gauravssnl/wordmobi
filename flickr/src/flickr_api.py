#! /usr/bin/env python
# Copyright (C) 2009  Raymond Sneekes (raymond@sneek.es)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import urllib
import simplejson as json

API_HOST = 'http://api.flickr.com'
API_PATH = '/services/rest/'
PHOTO_HOST = 'http://www.flickr.com'
PHOTO_PATH = '/photos/'

class FlickrObject:
    """
        Simple wrapper object for json dicts.
    """
    def __init__(self, dict):
        """
            Init with json generated dict
        """
        self.dict = dict

    def __getattr__(self, attribute):
        """
            Return requested attribute
        """
        if self.dict.has_key(attribute):
            ret = self.dict[attribute]
        elif attribute == '__repr__' or attribute == '__str__':
            def method(_self = self, _method = attribute, **params):
                return self.dict.__str__()
            return method
        else:
            return None

        if isinstance(ret, list):
            # convert objects in list
            lst = []
            for i in ret:
                lst.append(FlickrObject(i))
            return lst
        elif isinstance(ret, dict):
            # create new object if ret is dict
            return FlickrObject(ret)
        else:
            # just return the value
            return ret

class Flickr:
    """ 
        Simple Flickr functions
    """
    def __init__(self, api_key = None):
        self.api_key = api_key

    def __getattr__(self, method):
        def method(_self = self, _method = method, **params):
            _method = 'flickr.' + _method.replace('_', '.')

            data = self.get_data(_method, params)
            res = json.loads(data[14:-1])
            if res['stat'] == 'ok':
                return res
            else:
                return None

        return method

    def return_result(self, result, key_name):
        """
            Return new object if key_name is present in the result
        """
        if not None is result and result.has_key(key_name):
            return FlickrObject(result[key_name])
        else:
            return None

    def get_data(self, method, parameters):
        # default parameters
        parameters['method'] = method
        parameters['api_key'] = self.api_key
        parameters['format'] = 'json'
        url = '%s%s?%s' % (API_HOST, API_PATH, urllib.urlencode(parameters))

        opener = urllib.FancyURLopener()
        f = opener.open(url)
        data = f.read()
        f.close()

        return data

    def get_user_id(self, search_string):
        """
            find user, by emailaddres is search_string contains @ by
            username otherwise
        """
        if search_string.find('@') >= 0:
            res = self.people_findByEmail(find_email = search_string)
        else:
            res  = self.people_findByUsername(username = search_string)

        return self.return_result(res, 'user')

    def get_photos(self, user_id, per_page=10, page = 1):
        """
            Get the public photos of the specified user_id
        """
        photos = self.people_getPublicPhotos(
                user_id = user_id, per_page = per_page, page = page
            )

        return self.return_result(photos, 'photos')

    def get_photo_sizes(self, photo_id):
        """
            Get the possible photo sizes
        """
        sizes = self.photos_getSizes(photo_id = photo_id)
        return self.return_result(sizes, 'sizes')

    def get_photo_info(self, photo_id):
        """
            Get detailed photo information
        """
        info = self.photos_getInfo(photo_id = photo_id)
        return self.return_result(info, 'photo')

    def get_photo_url(self, user_id, photo_id):
        """
            Construct photo url from user_id and photo_id
        """
        return '%s%s%s/%s' % (PHOTO_HOST, PHOTO_PATH, user_id, photo_id)
