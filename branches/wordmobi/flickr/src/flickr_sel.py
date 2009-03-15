# Copyright (c) 2009  Raymond Sneekes (raymond@sneek.es)
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

# PyS60
import appuifw
import e32
import key_codes

# other
import flickr_api as flickr

class FlickrSel:
    def __init__(self, email_address, api_key):
        self.title = u'Flickr'
        self.flickr = flickr.Flickr(api_key)
        self.page_size = 10
        self.page_number = 1
        self.return_value = None
        self.email_address = email_address

    def reset_title(self):
        appuifw.app.title = self.title

    def quit(self):
        self.app_lock.signal()

    def fill_list(self):
        appuifw.app.title = u'Updating...'
        self.photos = self.flickr.get_photos(
                self.user.id, self.page_size, self.page_number
                )
        list = []
        for p in self.photos.photo:
            list.append(p.title)
        self.lb_photos.set_list(list)
        self.reset_title()

    def page_next(self):
        if self.page_number < int(self.photos.total) / self.page_size:
            self.page_number += 1
            self.fill_list()
        else:
            appuifw.note(u'Already at last page')

    def page_previous(self):
        if self.page_number > 1:
            self.page_number -= 1
            self.fill_list()
        else:
            appuifw.note(u'Already at first page')

    def select_photo(self):
        self.photo = self.photos.photo[self.lb_photos.current()]
        self.sizes = self.flickr.get_photo_sizes(self.photo.id)
        list = []
        for size in self.sizes.size:
            s = u'%s (%sx%s)' % (size.label, size.width, size.height)
            list.append(s)
        self.lb_sizes.set_list(list)
        appuifw.app.body = self.lb_sizes

    def select_size(self):
        size = self.sizes.size[self.lb_sizes.current()]
        self.return_value = self.create_href(
                self.user, self.photo, size
                )
        self.quit()

    def create_href(self, user, photo, size):
        url = self.flickr.get_photo_url(user.id, photo.id)
        href = u'\n<a href="%s" target="_blank"><img border="0" src="%s" alt="%s" /></a>\n' % (
                url, size.source, photo.title
                )
        return href

    def run(self):
        appuifw.app.exit_key_handler = self.quit
        appuifw.app.title = self.title
        appuifw.app.menu = [
                (u'Next page', self.page_next),
                (u'Previous page', self.page_previous),
                (u'Quit', self.quit)
                ]

        # already setup initial sizes listbox
        self.lb_sizes = appuifw.Listbox([u''], self.select_size)

        # photoname list
        self.lb_photos = appuifw.Listbox([u''], self.select_photo)
        self.lb_photos.bind(key_codes.EKeyRightArrow, self.page_next)
        self.lb_photos.bind(key_codes.EKeyLeftArrow, self.page_previous)
        appuifw.app.body = self.lb_photos

        self.user = self.flickr.get_user_id(self.email_address)
        if self.user is None:
            appuifw.note(u'User not found!', 'error')
        else:
            self.fill_list()

            self.app_lock = e32.Ao_lock()
            self.app_lock.wait()

        return self.return_value
