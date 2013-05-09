#!/user/bin/python
# -*- coding:utf-8 -*-
# filename:dbhandle/redisdb.py


import redis

from config import redisconf

MAX_CONNECTIONS = 128

def new_pool(host=redisconf['host'], port=redisconf['port'], db=redisconf['dbn']):
    '''create a new pool to redis'''
    return redis.ConnectionPool(host=host, port=port, db=db, max_connections=MAX_CONNECTIONS)

_pool = None

def get_handler():
    global _pool
    if _pool is None:
        _pool = new_pool()
    return redis.Redis(connection_pool=_pool)




