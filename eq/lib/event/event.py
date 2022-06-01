#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
#

"""
 This module implements several event related methods.
"""

import datetime

__author__     = "Jorge Morgado"
__copyright__  = "Copyright (c)2014, Jorge Morgado"
__credits__    = []
__license__    = "unknown"
__version__    = "1.0.0"
__maintainer__ = "Jorge Morgado"
__email__      = "jorge (at) morgado (dot) ch"
__status__     = "Production"

# Database fields (order has to match DbEvent cols in dbevent.py)
F_ID          = 0
F_TS          = 1
F_SOURCE      = 2
F_EVENTID     = 3
F_LASTEVENTID = 4
F_TYPE        = 5
F_STATE       = 6
F_STATETYPE   = 7
F_LASTSTATE   = 8
F_COUNT       = 9
F_HANDLED     = 10
F_IPV4        = 11
F_IPV6        = 12
F_HOSTNAME    = 13
F_SERVICENAME = 14
F_DATE        = 15
F_TIME        = 16
F_MESSAGE     = 17

# Date and time format
DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H:%M:%S'

# Handled states (I mean, bits)
IGNORED   = 0   # 2^0 = 1
MAILSENT  = 1   # 2^1 = 2
SMSSENT   = 2   # 2^2 = 4
#ETC...   = 3   # 2^3 = 8
#ETC...   = 4   # 2^4 = 16

# The meaning for 'handled' states:
#        .------ SMSSENT
#       /  .---- MAILSENT
#      /  /  .-- IGNORED
#     /  /  /
# 2^( 2  1  0 )
#     4  2  1
# ------------------------------------------------------------------------
#  0  0  0  0  Event is unhandled
#  1  0  0  1  Event is ignored
#  2  0  1  0  Event was sent via email
#     0  1  1  Invalid state (can't be ignored and mailsent)
#  4  1  0  0  Event was sent via SMS
#     1  0  1  Invalid state (can't be ignored and smssent)
#  6  1  1  0  Event was sent via email and SMS
#     1  1  1  Invalid state (can't be ignored and another non-ignored)

class Event():
    'Common base class for the event entity.'

    def __init__(self, row):
        """ Initialize the event object.
        """

        self.e = row
        self.h = self.__column(F_HANDLED)


    def __column(self, index):
        """ Return the value in the column given by index. It should always
            return some valid value, unless the cursor is not in a valid
            row - in this case None will be returned (although, it shoudn't).
        """
        if self.e is None:
            return None
        elif self.e[index] is None:
            return ''
        else:
            return self.e[index]


    def __str__(self):
        """ Return the event as string for pretty-printing.
        """

        return \
            "ID:           %d\n" \
            "Timestamp:    %s\n" \
            "Source:       %s\n" \
            "EventID:      %d\n" \
            "Last EventID: %d\n" \
            "Handled:      %d\n" \
            "Type:         %s\n" \
            "State:        %s\n" \
            "State type:   %s\n" \
            "Last state:   %s\n" \
            "Count:        %d\n" \
            "IPv4:         %s\n" \
            "Hostname:     %s\n" \
            "Service name: %s\n" \
            "Date:         %s\n" \
            "Time:         %s\n" \
            "Weekday:      %s\n" \
            "Message:      %s" % (
            self.id(),
            str(self.ts()),
            self.source(),
            self.eventid(),
            self.lasteventid(),
            self.handled(),
            self.type(),
            self.state(),
            self.statetype(),
            self.laststate(),
            self.count(),
            self.ipv4(),
            self.hostname(),
            self.servicename(),
            self.date(),
            self.time(),
            self.weekday(),
            self.message())


    def __is_bitset(self, n):
        """ Check if 'handled' has the n-th bit set.  """
        return (self.h & (1<<n)) != 0

    def __setbit(self, n):
        """ Set the 'handled' n-th bit. """
        self.h |= (1<<n)

    def __unsetbit(self, n):
        """ Unset the 'handled' n-th bit. """
        self.h &= ~(1<<n)


    def is_handled(self):
        """ If at least one bit is set, the event is handled. """
        return self.h != 0

    def is_ignored(self):
        """ Return True if the IGNORED bit is set. Otherwise, return False. """
        return self.__is_bitset(IGNORED)

    def is_mailsent(self):
        """ Return if the MAILSENT bit is set. Otherwise, return False. """
        return self.__is_bitset(MAILSENT)

    def is_smssent(self):
        """ Return if the SMSSENT bit is set. Otherwise, return False. """
        return self.__is_bitset(SMSSENT)


    def set_ignored(self):
        """ Mark the event as IGNORED. """
        self.__unsetbit(MAILSENT)
        self.__unsetbit(SMSSENT)
        self.__setbit(IGNORED)
        return self.h

    def set_mailsent(self):
        """ Mark the event as MAILSENT. """
        self.__unsetbit(IGNORED)
        self.__setbit(MAILSENT)
        return self.h

    def set_smssent(self):
        """ Mark the event as SMSSENT. """
        self.__unsetbit(IGNORED)
        self.__setbit(SMSSENT)
        return self.h


    # These should be used to get the field of the function with the same name.
    # For example, if the queue's cursor is in a valid row, you can get it's
    # ID by calling q.id(). To get the timestamp, call q.ts(), and so on...
    def id(self):          return self.__column(F_ID)
    def ts(self):          return self.__column(F_TS)
    def source(self):      return self.__column(F_SOURCE)
    def eventid(self):     return self.__column(F_EVENTID)
    def lasteventid(self): return self.__column(F_LASTEVENTID)
    def type(self):        return self.__column(F_TYPE)
    def state(self):       return self.__column(F_STATE)
    def statetype(self):   return self.__column(F_STATETYPE)
    def laststate(self):   return self.__column(F_LASTSTATE)
    def count(self):       return self.__column(F_COUNT)
    def handled(self):     return self.h
    def ipv4(self):        return self.__column(F_IPV4)
    def ipv6(self):        return self.__column(F_IPV6)
    def hostname(self):    return self.__column(F_HOSTNAME)
    def servicename(self): return self.__column(F_SERVICENAME)
    def date(self):        return self.__column(F_DATE)
    def time(self):        return self.__column(F_TIME)
    def message(self):     return self.__column(F_MESSAGE)

    def weekday(self):
        """ Return the weekday of the event.
        """

        wd = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday' ]

        return wd[datetime.datetime.strptime(self.date(), DATE_FMT).weekday()]


    def time_is_between(self, hr1, min1, hr2, min2):
        """ Return True if event's time is between hr1:min1 and hr2:min2.
        """

        time = datetime.datetime.strptime(self.date() + ' ' + self.time(),
                                          DATE_FMT + ' ' + TIME_FMT)
        time_min = time.replace(hour=hr1, minute=min1, second=0, microsecond=0)
        time_max = time.replace(hour=hr2, minute=min2, second=0, microsecond=0)

        return time_min < time < time_max


    def weekday_is_equal(self, weekday):
        """ Return True if event's week day is weekday.
        """

        # Convert to lowercase and substring only the first 3 characters
        return (self.weekday().lower()[:3] == weekday.lower()[:3])
