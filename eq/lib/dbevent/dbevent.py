#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
#

"""
A MySQL database layer abstraction for the `event` queue project database.

You must setup a MySQL database instance (and account) on the localhost as
follows:

CREATE DATABASE event;
USE event;
CREATE TABLE queue (
       id INTEGER NOT NULL AUTO_INCREMENT,
       ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       source VARCHAR(255) NOT NULL,
       type VARCHAR(255) NOT NULL,
       state VARCHAR(255) DEFAULT NULL,
       statetype VARCHAR(255) DEFAULT NULL,
       laststate VARCHAR(255) DEFAULT NULL,
       count INTEGER DEFAULT 1,
       handled BOOLEAN NOT NULL DEFAULT FALSE,
       ipv4 INT UNSIGNED DEFAULT NULL,
       ipv6 BINARY(16) DEFAULT NULL,
       hostname VARCHAR(255) DEFAULT NULL,
       servicename VARCHAR(255) DEFAULT NULL,
       date VARCHAR(30) NOT NULL,
       time VARCHAR(30) NOT NULL,
       message TEXT,
       PRIMARY KEY (id));

CREATE INDEX ts_idx ON queue(ts);
CREATE INDEX source_idx ON queue(source);
CREATE INDEX state_idx ON queue(state);
CREATE INDEX handled_idx ON queue(handled);
CREATE INDEX ipv4_idx ON queue(ipv4);
CREATE INDEX ipv6_idx ON queue(ipv6);
CREATE INDEX hostname_idx ON queue(hostname);

CREATE USER 'qapi'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES
      ON event.*
      TO 'qapi'@'localhost'
      WITH GRANT OPTION;
FLUSH PRIVILEGES;


To test the module use:
$ python dbevent.py
"""

import sys
sys.path.append('..')
from db.db import Db

__author__ = "Jorge Morgado"
__copyright__ = "Copyright (c)2014, Jorge Morgado"
__credits__ = []
__license__ = "unknown"
__version__ = "1.0.0"
__maintainer__ = "Jorge Morgado"
__email__ = "jorge (at) morgado (dot) ch"
__status__ = "Production"

class DbEvent():
    def __init__(self):
        """ Connect to the event queue database.

        >>> mydbevent = DbEvent()
        """

        # TODO Get user/password/host/dbname from configuration file
        # TODO instead of having them hardcoded here.
        self.db = Db('qapi', 'password', 'event')

        # Database columns (used for select clauses below)
        # Ordering has to match with indexes F_* in event.py
        self.cols = [
            'id',
            'ts',
            'source',
            'eventid',
            'lasteventid',
            'type',
            'state',
            'statetype',
            'laststate',
            'count',
            'handled',
            'INET_NTOA(`ipv4`) as ipv4',
            'ipv6',
            'hostname',
            'servicename',
            'date',
            'time',
            'message',
        ]


    def __del__(self):
        """ Close the database connection.

        >>> mydbevent = DbEvent()
        """

        del self.db


    def find_next(self):
        """ Get the next record from the cursor position. If no more records
            are available, return None.
        """

        return self.db.fetch_next()


    def __find_if_existing(self, source, etype, state, statetype, ipv4, ipv6, hostname, servicename):
        """ Search an unhandled event if it exists.
        """

        self.db.select('queue', ['id'], {
            'handled'    : ['=', '%(handled)s', '0'],
            'source'     : ['=', '%(source)s', source],
            'type'       : ['=', '%(type)s', etype],
            'state'      : ['=', '%(state)s', state],
            'statetype'  : ['=', '%(statetype)s', statetype],
            # TODO validate based on IPv4 and IPv6
            'ipv4'       : ['=', '%(ipv4)s', ipv4],
            'ipv6'       : ['=', '%(ipv6)s', ipv6],
            'hostname'   : ['=', '%(hostname)s', hostname],
            'servicename': ['=', '%(servicename)s', servicename],
            })
        row = self.db.fetch_next()

        return row[0] if row is not None else None


    def __find_duplicate(self, source, eventid, lasteventid, etype, state, hostname, servicename):
        """ Search the queue if the event already exists (duplicate).
            If found, returns the record's id; otherwise, returns None.

        >>> mydbevent = DbEvent()
        >>> mydbevent._DbEvent__find_duplicate('nagios1', 1, 0, 'RECOVERY', 'OK', 'office-gw', 'svc-name') > 0
        True
        >>> mydbevent._DbEvent__find_duplicate('nagios1', 1, 0, 'RECOVERY', 'OK', 'badhost', 'svc-name') is None
        True
        """

        self.db.select('queue', ['id'], {
            'source'      : ['=', '%(source)s', source],
            'eventid'     : ['=', '%(eventid)s', eventid],
            'lasteventid' : ['=', '%(lasteventid)s', lasteventid],
            'type'        : ['=', '%(type)s', etype],
            'state'       : ['=', '%(state)s', state],
            'hostname'    : ['=', '%(hostname)s', hostname],
            'servicename' : ['=', '%(servicename)s', servicename],
            })
        row = self.db.fetch_next()

        return row[0] if row is not None else None


    def __find_duplicate_without_names(self, source, eventid, lasteventid, etype, state):
        """ Search the queue if the event already exists (duplicate).
            If found, returns the record's id; otherwise, returns None.
            Similar to __find_duplicate() but not checking hostname/servicename (e.g. for Heartbeats)

        >>> mydbevent = DbEvent()
        >>> mydbevent._DbEvent__find_duplicate_without_names('nagios1', 1, 0, 'RECOVERY', 'OK') > 0
        True
        >>> mydbevent._DbEvent__find_duplicate_without_names('badnagios', 1, 0, 'RECOVERY', 'OK') is None
        True
        """

        self.db.select('queue', ['id'], {
            'source'      : ['=', '%(source)s', source],
            'eventid'     : ['=', '%(eventid)s', eventid],
            'lasteventid' : ['=', '%(lasteventid)s', lasteventid],
            'type'        : ['=', '%(type)s', etype],
            'state'       : ['=', '%(state)s', state],
            })
        row = self.db.fetch_next()

        return row[0] if row is not None else None


    def increase_count(self, _id):
        """ Increment the event count for the sepecified `id`.

        >>> mydbevent = DbEvent()
        >>> mydbevent.increase_count(5)
        True
        """

        return self.db.update('queue',
            { 'count': 'count + 1', },
            { 'id': [ '%(id)s', _id ] })


    def set_handled(self, _id, handled):
        """ Set the event handled value to Yes/No (True/False).
        """

        return self.db.update('queue',
            { 'handled': str(handled) },
            { 'id': [ '%(id)s', _id ] })


    def new_heartbeat_event(self, source, etype, state, date, time):
        """ Insert a new heartbeat event in the `queue` table. If the event
            already exists, i.e., is *not* new, it will just increment the
            event count.
        """

        # See if the event already exists (must have the same source,
        # event id, type and state)
        _id = self.__find_duplicate_without_names(source, 0, 0, etype, state)

        if _id is None:
            return self.db.insert('queue', {
                  'source' : [ '%(source)s',  source ],
                  'type'   : [ '%(type)s',    etype  ],
                  'state'  : [ '%(state)s',   state  ],
                  'handled': [ '%(handled)s', 1      ],
                  'date'   : [ '%(date)s',    date   ],
                  'time'   : [ '%(time)s',    time   ],
                })
        else:
            return self.db.update('queue',
                { # Update fileds
                  'ts':    'CURRENT_TIMESTAMP',
                  'count': 'count + 1',
                },
                { # Update criteria
                  'id': [ '%(id)s', _id ]
                })


    def new_event(self, source, eventid, lasteventid, etype, state, \
        statetype, laststate, ipv4, ipv6, hostname, servicename, date, time, message):
        """ Insert a new event in the `queue` table. If the event already
            exists, i.e., is *not* new, it will just increment the event count.

        >>> mydbevent = DbEvent()
        >>> mydbevent.new_event('nagios1', 1, 0, 'RECOVERY', 'OK', 'HARD', 'WARNING', \
                '192.168.1.1', None, 'office-gw', 'svc-name', '2014-06-10', '17:33:00', \
                'Load too high') > 0
        True
        >>> mydbevent.new_event('nagios1', 1, 0, 'RECOVERY', 'OK', 'HARD', 'WARNING', \
                '192.168.1.1', None, 'office-gw', 'svc-name', '2014-06-10', '17:34:00', \
                'Load too high') > 0
        True
        """

        # See if the event already exists (must have the same source,
        # event id, type and state)
        _id = self.__find_duplicate(source, eventid, lasteventid, etype, state, hostname, servicename)

        if _id is None:
            _id = self.db.insert('queue', {
                      'source'     : [ '%(source)s',          source      ],
                      'eventid'    : [ '%(eventid)s',         eventid     ],
                      'lasteventid': [ '%(lasteventid)s',     lasteventid ],
                      'type'       : [ '%(type)s',            etype       ],
                      'state'      : [ '%(state)s',           state       ],
                      'statetype'  : [ '%(statetype)s',       statetype   ],
                      'laststate'  : [ '%(laststate)s',       laststate   ],
                      'ipv4'       : [ 'INET_ATON(%(ipv4)s)', ipv4        ],
                      'ipv6'       : [ '%(ipv6)s',            ipv6        ],
                      'hostname'   : [ '%(hostname)s',        hostname    ],
                      'servicename': [ '%(servicename)s',     servicename ],
                      'date'       : [ '%(date)s',            date        ],
                      'time'       : [ '%(time)s',            time        ],
                      'message'    : [ '%(message)s',         message     ],
                      })
        else:
            self.increase_count(_id)

        return _id


    def find_all(self, ts_max):
        """ Get a cursor for all events.
            If no records are found, returns returns None.

        >>> mydbevent = DbEvent()
        >>> row = mydbevent.find_all(500)
        >>> while row is not None: \
            row = mydbevent.find_next()
        """

        self.db.select('queue', self.cols,
            { # Select criteria
              'ts': [ '<', '%(ts)s', ts_max ],
            },
            [ 'id' ])    # Ordered by...

        return self.db.fetch_next()


    def find_heartbeat(self, ts_max):
        """ Get a cursor for all heartbeat events.
            If no records are found, returns returns None.
        """

        self.db.select('queue', self.cols,
            { # Select criteria
              'ts'  : [ '<',  '%(ts)s',   ts_max      ],
              'type': [ '=', '%(type)s', 'HEARTBEAT' ],
            },
            [ 'id' ])   # Ordered by...

        return self.db.fetch_next()


    def find_all_unhandled(self, ts_max):
        """ Get a cursor for all unhandled events.
            If no records are found, returns returns None.

        >>> mydbevent = DbEvent()
        >>> row = mydbevent.find_all_unhandled(500)
        >>> while row is not None: \
            row = mydbevent.find_next()
        """

        self.db.select('queue', self.cols,
            { # Select criteria
              'ts'     : [ '<', '%(ts)s',      ts_max ],
              'handled': [ '=', '%(handled)s', '0'    ],
            },
            [ 'id' ])   # Ordered by...

        return self.db.fetch_next()


    def find_eventid(self, source, eventid):
        """ Find an event based on source and event ID.
        """

        self.db.select('queue', self.cols,
            where={
              'source' : [ '=', '%(source)s',  source ],
              'eventid': [ '=', '%(eventid)s', eventid ],
            },
            order=[ 'id' ],
            desc=True)

        return self.db.fetch_next()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
