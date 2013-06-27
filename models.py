#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import logging
import os
import sys

sys.path.append(os.path.split(os.path.dirname(__file__))[0])
from dbhandler import mongohandler
'''
users{
"id":23123,
"username":"",
"access_token":"",
"facebook":{...},
"twitter":{...},
"linkedin":{...},
"intagram":{...}
}
'''

_MONGO = mongohandler.MongoHandler().db


def update_user_evernote(id, username, access_token):
    rowcount = 0
    _filter = {"id":id, "username":username}
    _set = {"access_token":access_token}
    res = _MONGO.users.update( _filter, {"$set":_set}, upsert=True, w=1)
    if res["n"] :
        rowcount = res["n"]
    else:
        logging.error( "update_user_evernote failed:**%s**  %s" ,
                       res, str(zip(id,username,access_token)))
    return rowcount


def update_user_guid(id, guid):
    rowcount = 0
    _filter = {"id":id}
    _set = {"guid":guid}
    res = _MONGO.users.update( _filter, {"$set":_set}, w=1)
    if res["n"] :
        rowcount = res["n"]
    return rowcount


def get_user_guid(id):
    res =  _MONGO.users.find_one( {"id":id},{"guid":1} )
    guid = res.get("guid",None)
    return guid
    
def get_user_token( id ):
    try:
        res =  _MONGO.users.find_one( {"id":id},
                                    {"access_token":1} )
        access_token = res["access_token"]
    except:
        access_token = None
    return access_token


def get_facebook_token( enid ):
    try:
        res =  _MONGO.users.find_one( {"id":enid},
                                    {"facebook":1} )
        access_token = res['facebook']["access_token"]
        fbid = res['facebook']["id"]
    except:
        access_token = None
        fbid = None
    return fbid, access_token

def get_twitter_token(enid):
    try:
        res =  _MONGO.users.find_one( {"id":enid},
                                    {"twitter":1} )
        access_token = res['twitter']["access_token"]
        twid = res['twitter']["id"]
    except:
        access_token = None
        twid = None
    return twid, access_token
    

def get_foursquare_token(enid):
    try:
        res =  _MONGO.users.find_one( {"id":enid},
                                    {"foursquare":1} )
        access_token = res['forusquare']["access_token"]
        sqid = res['foursquare']["id"]
    except:
        access_token = None
        sqid = None
    return sqid, access_token
    
def get_sns_token(enid, source):
    ''''get token filter with sns source
    return sns id and access_token'''
    try:
        res =  _MONGO.users.find_one( {"id":enid},
                                    {source:1} )
        access_token = res[source]["access_token"]
        _id = res[source]["id"]
    except:
        access_token = None
        _id = None
    return _id, access_token
    

def get_user(enid):
    try:
        res =  _MONGO.users.find_one( {"id":enid})
    except:
        res  = None
    return res
    

def update_user_sns(id, user, sns_tag):
    "saving connect user sns."
    rowcount = 0
    _filter = {"id":id}
    _set = {sns_tag:user}
    res = _MONGO.users.update( _filter, {"$set":_set},  w=1)
    if res["n"] :
        rowcount = res["n"]
    return rowcount
    
def save_daily(data):
    rowcount = 0
    res = _MONGO.daily.insert(data)
    if res:
        rowcount = len(res)
    return rowcount


def update_daily(id,date,daily,type_tag):
    rowcount = 0
    _filter = {"id":id, "date":date}
    _set = {type_tag:daily}
    res = _MONGO.daily.update( _filter, {"$set":_set}, upsert=True, w=1)
    if res["n"] :
        rowcount = res["n"]
    else:
        logging.error( "update_daily failed:**%s**  %s" ,
                       res, str(zip(id, date, daily, type_tag)) )
    return rowcount
    

def get_since_id(enid, twid):
    _filter = {"id":enid, "sid":twid}
    _field = {"ddid":1}
    _sort = [("created_time",-1)]
    try:
        print _filter
        res =  _MONGO.daily.find( _filter, _field, sort=_sort, limit=1)
        since_id = res[0]["ddid"]
    except:
        since_id = 0
    return since_id










