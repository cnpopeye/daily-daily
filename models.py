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
