#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
import time


def get_since_until(date):
    '''
    date must be UTC timestamp,
    return since and until as timestamp'''
    try:
        the_day = datetime.fromtimestamp(date)
        if not isinstance(the_day, datetime):
            return None,None
        until_date = the_day + timedelta(days=1)
        since = int(time.mktime(the_day.timetuple()) )
        until = int(time.mktime(until_date.timetuple()) )
    except Exception,e:
        print e
        return None, None
    return since, until
