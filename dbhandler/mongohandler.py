#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pymongo
import sys
from config import mongo

class MongoHandler():
    '''
    封装mongodb链接对象
    获取对象之后,可自由操作
    '''
    def __init__( self, host = mongo["host"], port = mongo["port"], db = mongo["dbn"], user = mongo["user"], passwd = mongo["passwd"],
                    max_pool_size = mongo["max_pool_size"] ):
        try:
            self.connection = pymongo.Connection( host = host, port = port , max_pool_size = max_pool_size )
            if not db:
                db = 'test'
            self.db = self.connection[db]
            if user:
                self.db.authenticate( user, passwd )
            print "mogodb init ok."
        except Exception, e:
            print "mongodb init error:" + str( e )
            sys.exit( 1 )



