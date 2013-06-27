#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import tornado.web
import tornado.auth
from tornado import httpserver, ioloop
from tornado.options import define, options
from tornado_api import FoursquareMixin
import config as conf
import controller as ctr
import utils as u

'''
Created on 2013-1-11

@author: cn.popeye

'''

define("port", default=8999, help="run on the given port", type=int)

app_root = os.path.dirname( __file__ )

settings = dict(
    template_path = os.path.join(os.path.dirname(__file__),"templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    debug = True,
    xsrf_cookies = False,
    cookie_secret = "QHd1emhhbmdodXpodWdlemhvbmdAcXVkaWFu",
    autoescape = None,
    login_url = "/login",
    twitter_consumer_key = conf.twitter_consumer_key,
    twitter_consumer_secret = conf.twitter_consumer_secret,
 )


class BaseHandler( tornado.web.RequestHandler ):
    def get_current_user( self ):
        return self.get_secure_cookie( "id", None )

class LoginWithEvernote(BaseHandler):
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
        u_id_name = dict(id=user.id, uname = user.username)
        self.finish(u_id_name)


class ConnectFacebook(BaseHandler,
                      tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        enid = self.get_current_user()
        if not enid:
            self.redirect("/login")

        my_url = (self.request.protocol + "://" + self.request.host +
                  "/connect/facebook")
        if self.get_argument("code", False):
            self.get_authenticated_user(
                   redirect_uri=my_url,
                   client_id=conf.facebook_api_key,
                   client_secret=conf.facebook_secret,
                   code=self.get_argument("code"),
                   extra_fields=set(["timezone"]),
                   callback= self.async_callback(self._on_auth, enid) ) 
            return
        self.authorize_redirect(
                 redirect_uri=my_url,
                 client_id=conf.facebook_api_key,
                 extra_params={"scope": "read_stream,offline_access"} )
      
    def _on_auth(self, enid, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed.")
        if not ctr.connect_facebook(int(enid), user):
            raise tornado.web.HTTPError(500, "save facebook failed.")
        self.finish(user)

    
class ConnectTwitter(BaseHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        enid = self.get_current_user()
        if not enid:
            self.redirect("/login")

        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(
                           self.async_callback(self._on_auth, enid) )
            return
        self.authorize_redirect()

    def _on_auth(self, enid, user):
        if not user:
            raise tornado.web.HTTPError(500, "Twitter auth failed")
        if not ctr.connect_twitter(int(enid), user):
            raise tornado.web.HTTPError(500, "save twitter failed.")
        self.finish(user)


class ConnectFoursquare(BaseHandler, FoursquareMixin):
    @tornado.web.asynchronous
    def get(self):
        enid = self.get_current_user()
        if not enid:
            self.redirect("/login")

        my_url = (self.request.protocol + "://" + self.request.host +
                  "/connect/foursquare")

        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=conf.foursquare_client_id,
                client_secret=conf.foursquare_client_secret,
                code=self.get_argument("code"),
                callback=self.async_callback(self._on_auth, enid)
                )
            return

        self.authorize_redirect(
            redirect_uri=my_url,
            client_id=conf.foursquare_client_id
        )

    def _on_auth(self, enid, user):
        if not user:
            raise tornado.web.HTTPError(500, "Foursquare auth failed")
        if not ctr.connect_foursquare(int(enid), user):
            raise tornado.web.HTTPError(500, "save foursquare failed.")

        self.finish(user)


class ConnectInstagram(tornado.web.RequestHandler):
    def get(self):
        pass


class DailyFacebook(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self, enid, special_timestamp):
        fbid, access_token = ctr.get_facebook_token(int(enid))
        if not fbid or not access_token:
            return
        since, until = u.get_since_until(int(special_timestamp) )
        if not since or not until:
            return
        fields=set(["created_time","id","message","full_picture",
                    "description"])
        self.facebook_request(
                             path="/%s/feed" % fbid,
                             access_token= access_token,
                             callback=self.async_callback(
                                            self._on_get_daily,
                                            int(enid) ),
                             since=since,
                             until=until,
                             limit=1000,
                             fields=",".join(fields)
                          )

    def _on_get_daily(self, enid, daily):
        if daily:
            ctr.update_daily_facebook(enid, daily)
        self.finish(daily)

        
class DailyTwitter(BaseHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self, enid):
        _enid = int(enid)
        twid, access_token = ctr.get_twitter_token(_enid)
        if not twid or not access_token:
            return
        params = dict(
                user_id = twid,
                count=200,
                trim_user=True,
                include_entities=True
                )
        
        since_id=ctr.get_since_id(_enid, twid)
        if since_id:
            params.update(since_id=since_id)
        self.twitter_request(
                path="/statuses/user_timeline",
                access_token=access_token,
                callback=self.async_callback(self._on_get_daily,
                                             _enid,
                                             twid),
                **params
                )

    def _on_get_daily(self, enid, twid, daily):
        if daily:
            ctr.update_daily_twitter(enid, twid, daily)
        self.finish()


class Dailyfoursquare(BaseHandler, FoursquareMixin):
    @tornado.web.asynchronous
    def get(self, enid, special_timestamp):
        _enid = int(enid)
        foursquare_id, access_token = ctr.get_foursquare_token(_enid)
        if not foursquare_id or not access_token:
            return
        since, until = u.get_since_until(int(special_timestamp) )

        params = dict(
                limit=200,
                sort="oldestfirst",
                afterTimestamp = since,
                beforeTimestamp = until,
                )
        
        self.foursquare_request(
                path="users/self/checkins",
                callback=self.async_callback(self._on_get_daily,
                                             enid,
                                             foursquare_id
                                             ),
                access_token=access_token,
                **params
                )

    def _on_get_daily(self, enid, foursquare_id, daily):
        if daily:
            ctr.update_daily_foursuare(enid, foursquare_id, daily)
        self.finish()

        
urls = [
        ( r"/login", LoginWithEvernote),
        ( r"/connect/facebook", ConnectFacebook ),
        ( r"/connect/twitter", ConnectTwitter ),
        ( r"/connect/foursquare", ConnectFoursquare ),
        ( r"/connect/instagram", ConnectInstagram ),
        ( r"/daily/facebook/(\d+)/(\d+)", DailyFacebook ),
        ( r"/daily/twitter/(\d+)", DailyTwitter ),
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


