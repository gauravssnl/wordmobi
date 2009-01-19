"""
	wordpresslib.py
	
	WordPress xml-rpc client library
	use MovableType API
	
	Copyright (C) 2005 Michele Ferretti
	black.bird@tiscali.it
	http://www.blackbirdblog.it
	
	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	
	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA	02111-1307, USA.

	XML-RPC supported methods: 
		* getUsersBlogs
		* getUserInfo
		* getPost
		* getRecentPosts
		* getLastPostTitle		
		* getRecentPostTitles		
		* newPost
		* editPost
		* deletePost
		* newMediaObject
		* getCategoryList
		* getPostCategories
		* setPostCategories
		* getTrackbackPings
		* publishPost
		* getPingbacks
		* getCommentCount
		* getComments
		* getComment

	References:
		* http://codex.wordpress.org/XML-RPC_Support
		* http://www.sixapart.com/movabletype/docs/mtmanual_programmatic.html
		* http://docs.python.org/lib/module-xmlrpclib.html
"""

__author__ = "Michele Ferretti <black.bird@tiscali.it>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2005/05/02 $"
__copyright__ = "Copyright (c) 2005 Michele Ferretti"
__license__ = "LGPL"

import exceptions
import re
import os
import xmlrpclib
#import datetime
import time

class WordPressException(exceptions.Exception):
    """Custom exception for WordPress client operations
    """
    def __init__(self, obj):
        if isinstance(obj, xmlrpclib.Fault):
            self.id = obj.faultCode
            self.message = obj.faultString
        else:
            self.id = 0
            self.message = obj

    def __str__(self):
        return '<%s %d: \'%s\'>' % (self.__class__.__name__, self.id, self.message)
        
class WordPressBlog:
    """Represents blog item
    """ 
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False

class WordPressComment:
    """Represents comment item
    """ 
    def __init__(self):
        self.post_id = ''
        self.status = ''
        self.offset = 0
        self.number = 10

class WordPressEditComment:
    """Represents comment item for editing
    """ 
    def __init__(self):
        self.status = ''
        self.date_created_gmt = ''
        self.content = ''
        self.author = ''
        self.author_url = ''
        self.author_email = ''

class WordPressNewComment:
    """Represents a new comment 
    """ 
    def __init__(self):
        self.status = ''
        self.content = ''
        self.author = ''
        self.author_url = ''
        self.author_email = ''
        
class WordPressUser:
    """Represents user item
    """ 
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.email = ''
        
class MovableTypeCategory:
    """Represents category item
    """ 
    def __init__(self):
        self.id = 0
        self.name = ''
        self.isPrimary = False

class WordPressCategory:
    """Represents category item
    """ 
    def __init__(self):
        self.categoryId = 0
        self.parentId = 0
        self.categoryName = ''
        self.description = ''

class WordPressNewCategory:
    def __init__(self):
        self.name = ''
        self.slug = ''
        self.parent_id = 0
        self.description = ''
        
class WordPressPost:
    """Represents post item
    """ 
    def __init__(self):
        self.id = 0
        self.title = ''
        self.date = None
        self.permaLink = ''
        self.description = ''
        self.textMore = ''
        self.excerpt = ''
        self.link = ''
        self.user = ''
        self.allowPings = False
        self.allowComments = False

        
class WordPressClient:
    """Client for connect to WordPress XML-RPC interface
    """
    
    def __init__(self, url, user, password, transport=None):
        self.url = url
        self.user = user
        self.password = password
        self.blogId = 0
        self.transport = transport
        self._server = xmlrpclib.ServerProxy(self.url,self.transport)

    def _filterPost(self, post):
        """Transform post struct in WordPressPost instance 
        """
        postObj = WordPressPost()
        postObj.permaLink       = post['permaLink']
        postObj.description     = post['description']
        postObj.title           = post['title']
        postObj.excerpt         = post['mt_excerpt']
        postObj.user            = post['userid']
        postObj.date            = time.strptime(str(post['dateCreated']), "%Y%m%dT%H:%M:%S")
        postObj.link            = post['link']
        postObj.textMore        = post['mt_text_more']
        postObj.allowComments   = post['mt_allow_comments'] == 1
        postObj.id              = int(post['postid'])
        postObj.categories      = post['categories']
        postObj.allowPings      = post['mt_allow_pings'] == 1
        return postObj
		
    def _filterCategory(self, cat):
        """Transform category struct in MovableTypeCategory instance
        """
        catObj = MovableTypeCategory()
        catObj.id           = int(cat['categoryId'])
        catObj.name         = cat['categoryName'] 
        if cat.has_key('isPrimary'):
            catObj.isPrimary    = cat['isPrimary']
        return catObj
		
    def selectBlog(self, blogId):
        self.blogId = blogId
        
    def supportedMethods(self):
        """Get supported methods list
        """
        return self._server.mt.supportedMethods()

    def getLastPost(self):
        """Get last post
        """
        return tuple(self.getRecentPosts(1))[0]
            
    def getRecentPosts(self, numPosts=5):
        """Get recent posts
        """
        try:
            posts = self._server.metaWeblog.getRecentPosts(self.blogId, self.user,self.password, numPosts)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return posts

    def getLastPostTitle(self):
        """Get last post title
        """
        return tuple(self.getRecentPostTitles(1))[0]
        
    def getRecentPostTitles(self, numPosts = 5):
        """Get recent post titles
        """
        try:
            postTitles = self._server.mt.getRecentPostTitles(self.blogId, self.user,self.password, numPosts)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return postTitles
    
    def getPost(self, postId):
        """Get post item
        """
        try:
            #return self._filterPost(self._server.metaWeblog.getPost(str(postId), self.user, self.password))
            return self._server.metaWeblog.getPost(str(postId), self.user, self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
		
    def getUserInfo(self):
        """Get user info
        """
        try:
            userinfo = self._server.blogger.getUserInfo('', self.user, self.password)
            userObj = WordPressUser()
            userObj.id = userinfo['userid']
            userObj.firstName = userinfo['firstname']
            userObj.lastName = userinfo['lastname']
            userObj.nickname = userinfo['nickname']
            userObj.email = userinfo['email']
            return userObj
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
			
    def getUsersBlogs(self):
        """Get blog's users info
        """
        try:
            blogs = self._server.blogger.getUsersBlogs('', self.user, self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        blogObj = []
        for blog in blogs:
            bo = WordPressBlog()
            bo.id = blog['blogid']
            bo.name = blog['blogName']
            bo.isAdmin = blog['isAdmin']
            bo.url = blog['url']
            blogObj.append(bo)

        return blogObj

    def newPost(self, post, publish):
        """Insert new post
        """
        blogContent = {
            'title' : post.title,
            'description' : post.description    
        }
        
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1
        
        # insert new post
        try:
            idNewPost = int(self._server.metaWeblog.newPost(self.blogId, self.user, self.password, blogContent, 0))
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
        # set categories for new post
        try:
            self.setPostCategories(idNewPost, categories)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
                
        # publish post if publish set at True 
        if publish:
            try:
                self.publishPost(idNewPost)
            except xmlrpclib.Fault, fault:
                raise WordPressException(fault)                
            
        return idNewPost
       
    def getPostCategories(self, postId):
        """Get post's categories
        """
        try:
            categories = self._server.mt.getPostCategories(postId, self.user,self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        cats = []
        for c in categories:
            cats.append(self._filterCategory(c))

        return cats

    def setPostCategories(self, postId, categories):
        """Set post's categories
        """
        self._server.mt.setPostCategories(postId, self.user, self.password, categories)
    
    def editPost(self, postId, post, publish):
        """Edit post
        """
        blogcontent = {
            'title' : post.title,
            'description' : post.description,
            'permaLink' : post.permaLink,
            'mt_allow_pings' : post.allowPings,
            'mt_text_more' : post.textMore,
            'mt_excerpt' : post.excerpt
        }
        
        if post.date:
            blogcontent['dateCreated'] = xmlrpclib.DateTime(post.date) 
        
        # add categories
        i = 0
        categories = []
        for cat in post.categories:
            if i == 0:
                categories.append({'categoryId' : cat, 'isPrimary' : 1})
            else:
                categories.append({'categoryId' : cat, 'isPrimary' : 0})
            i += 1               

        try:
            result = self._server.metaWeblog.editPost(postId, self.user, self.password, blogcontent, 0)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)            
        
        if result == 0:
            raise WordPressException('Post edit failed')
            
        # set categories for new post
        try:
            self.setPostCategories(postId, categories)
        except:
            raise WordPressException('Category edit failed')
        
        # publish new post
        if publish:
            try:
                self.publishPost(postId)
            except:
                raise WordPressException('publish failed')

    def deletePost(self, postId):
        """Delete post
        """
        try:
            return self._server.blogger.deletePost('', postId, self.user, 
                                             self.password)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCategoryList(self):
        """Get blog's categories list
        """
        categories = []        
        try:
            cats = self._server.mt.getCategoryList(self.blogId, self.user, self.password) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        for cat in cats:
            categories.append(self._filterCategory(cat))
            
        return categories

    def getCategoryIdFromName(self, name):
        """Get category id from category name
        """
        for c in self.getCategoryList():
            if c.name == name:
                return c.id
        
    def getTrackbackPings(self, postId):
        """Get trackback pings of post
        """
        try:
            return self._server.mt.getTrackbackPings(postId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def publishPost(self, postId):
        """Publish post
        """
        try:
            return (self._server.mt.publishPost(postId, self.user, self.password) == 1)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getPingbacks(self, postUrl):
        """Get pingbacks of post
        """
        try:
            return self._server.pingback.extensions.getPingbacks(postUrl)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
            
    def newMediaObject(self, mediaFileName):
        """Add new media object (image, movie, etc...)
        """
        try:
            f = file(mediaFileName, 'rb')
            mediaBits = f.read()
            f.close()
            
            mediaStruct = {
                'name' : os.path.basename(mediaFileName),
                'bits' : xmlrpclib.Binary(mediaBits)
            }
            
            result = self._server.metaWeblog.newMediaObject(self.blogId, 
                                    self.user, self.password, mediaStruct)
            return result['url']
            
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

    def getCommentCount(self, post_id = ''):
        """Get the number of commands for a post or for the blog ( post_id = '' )
        """
        try:
            comments_cnt = self._server.wp.getCommentCount(self.blogId, self.user, self.password, post_id)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comments_cnt

    
    def getComment(self, commentId):
        """Get a comment
        """
        try:
            comment = self._server.wp.getComment(self.blogId, self.user, self.password, commentId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comment
    
    def getComments(self, commInfo):
        """Get comments for a given post. Use WordPressComment
        """
        try:
            comments = self._server.wp.getComments(self.blogId, self.user, self.password, commInfo)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comments

    def editComment(self, commentId, commEdit):
        """Get comments for a given post. Use WordPressCommentEdit
        """
        try:
            resp = self._server.wp.editComment(self.blogId, self.user, self.password, commentId, commEdit)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return resp

    def deleteComment(self, commentId):
        """Delete a comment
        """
        try:
            resp = self._server.wp.deleteComment(self.blogId, self.user, self.password, commentId)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return resp

    def newComment(self, postId, commentNew):
        """Insert a new comment
        """
        try:
            comment = self._server.wp.newComment(self.blogId, self.user, self.password, postId, commentNew)
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        return comment    

    def getCategories(self):
        """Get blog's categories list using wp
        """
        def filterCategory(cat):
            return { 'categoryId':cat['categoryId'],
                     'parentId':cat['parentId'],
                     'categoryName':cat['categoryName'],
                     'description':cat['description'] }

        cats = []
        try:
            wpcats = self._server.wp.getCategories(self.blogId, self.user, self.password) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)

        for c in wpcats:
            cats.append( filterCategory(c) )   

        return cats
        
    def newCategory(self,cat):
        try:
            cat_id = self._server.wp.newCategory(self.blogId, self.user, self.password, cat) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
        return cat_id

    def deleteCategory(self,cat_id):
        try:
            res = self._server.wp.deleteCategory(self.blogId, self.user, self.password, cat_id) 
        except xmlrpclib.Fault, fault:
            raise WordPressException(fault)
        
        return res
