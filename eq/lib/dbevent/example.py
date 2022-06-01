#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbevent import DbEvent

mydbevent = DbEvent()

row = mydbevent.find_all_unhandled(500)

while row is not None:
    print(row)
    row = mydbevent.find_next()

exit()
