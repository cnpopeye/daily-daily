#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado.web
from tornado import httpserver, ioloop
from tornado.options import define, options
import os
import config as conf
import controller as ctr
'''
Created on 2013-1-11

@author: cn.popeye

'''

define("port", default=8999, help="run on the given port", type=int)

app_root = os.path.dirname( __file__ )
static_path = os.path.join( app_root, "static" )
template_path = os.path.join( app_root, "templates" )

settings = dict(
    template_path = template_path,
    static_path = static_path,
    debug = True,
    xsrf_cookies = False,
    cookie_secret = "QHd1emhhbmdodXpodWdlemhvbmdAcXVkaWFu",
    autoescape = None,
    login_url = "/login",
 )


class LoginWithEvernote(tornado.web.RequestHandler):
    "auth evernote"
    @tornado.web.asynchronous
    def get(self):
        user_id = self.get_secure_cookie("id") if self.get_secure_cookie("id") else 0
        client = ctr.get_evernote_client_via_id( user_id  )
        if client.token:
            self._get_user(client.token,
                           self.async_callback(self._on_get_user) )
            return
        oauth_verifier = self.get_argument('oauth_verifier', None)
        if oauth_verifier:
            access_token = client.get_access_token(
                self.get_argument('oauth_token',None),
                self.get_secure_cookie('ots',None),
                oauth_verifier)
            self._get_user(access_token,
                           self.async_callback(self._on_get_user) )
            return
       
        request_token = client.get_request_token(conf.en_callback)
        self.set_secure_cookie('ots',request_token['oauth_token_secret'])
        authorized_url = client.get_authorize_url(request_token)
        self.redirect(authorized_url)

    def _get_user(self, access_token, callback):
        callback( access_token)
        
    def _on_get_user(self, access_token):
        "saving user and set cookie."
        user = ctr.update_user(access_token)
        if not user:
            raise tornado.web.HTTPError(500,"evernote auth failed!")
        self.set_secure_cookie("id", str(user.id) )
        u = dict(id=user.id, uname = user.username)
        self.finish(u)
        
class ConnectFacebook(tornado.web.RequestHandler):
    def get(self):
        pass

class ConnectTwitter(tornado.web.RequestHandler):
    def get(self):
        pass

class ConnectLinkedin(tornado.web.RequestHandler):
    def get(self):
        pass

class ConnectInstagram(tornado.web.RequestHandler):
    def get(self):
        pass
    
urls = [
        ( r"/login", LoginWithEvernote),
        ( r"/connect/facebook", ConnectFacebook ),
        ( r"/connect/twitter", ConnectTwitter ),
        ( r"/connect/linkedin", ConnectLinkedin ),
        ( r"/connect/instagram", ConnectInstagram ),
        ]

class Application( tornado.web.Application ):
    def __init__( self ):
        tornado.web.Application.__init__( self, urls, **settings )


def main():
    options.parse_command_line()
    http_server = httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen( options.port )
    print  "running DEBUG:%s ,port %d" % (settings['debug'], options.port)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    print "Starting server..."
    main()
    print "Started."
