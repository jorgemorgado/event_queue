#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import and_, or_
from sqlalchemy import func

# This is a circular import :-/
from eqweb import app

__author__     = 'Jorge Morgado'
__copyright__  = 'Copyright (c)2016'
__credits__    = []
__license__    = 'unknown'
__version__    = '1.0.0'
__maintainer__ = 'Jorge Morgado'
__email__      = 'jorge (at) morgado (dot) ch'
__status__     = 'Production'

db = SQLAlchemy(app)

from eqweb.db.models import User, Queue, Query


# def db_insert(name, entry):
#     try:
#         db.session.add(entry)
#         db.session.commit()
#     except IntegrityError:
#         raise Exception("%s already exists." % name)
#     except Exception as e:
#         raise e


# def db_callproc(proc, args):
#     connection = db.engine.raw_connection()
#
#     try:
#         cursor = connection.cursor()
#         cursor.callproc(proc, args)
#         data = cursor.fetchall()
#         cursor.close()
#         connection.commit()
#
#         return data
#     except Exception as e:
#         raise e
#     finally:
#         connection.close()


def db_get_userid(username):
    """ Return the user ID for the given username.

    If the number of records is higher than 1 (MultipleResultsFound) or
    if no rows were found, it returns None.
    """
    try:
        return User.query \
            .with_entities(User.id) \
            .filter_by(username=username) \
            .scalar()
    except MultipleResultsFound:
        return None


def db_get_event(id):
    """ Return the event details the given event ID.

    If the number of records is higher than 1 (MultipleResultsFound) or
    if no rows were found, it returns None.
    """
    try:
        return Queue.query \
            .filter_by(id=id) \
            .one()
    except MultipleResultsFound:
        return None


def db_queue_sources():
    """ Return the result of the following query:
    SELECT source FROM queue GROUP BY source ORDER BY source;
    """
    try:
        return Queue.query \
            .with_entities(Queue.source) \
            .group_by(Queue.source) \
            .order_by(Queue.source) \
            .all()
    except Exception as e:
        raise e


def db_queue_hostnames():
    """ Return the result of the following query:
    SELECT hostname FROM queue GROUP BY hostname ORDER BY hostname;
    """
    try:
        return Queue.query \
            .with_entities(Queue.hostname) \
            .group_by(Queue.hostname) \
            .order_by(Queue.hostname) \
            .all()
    except Exception as e:
        raise e


def db_queue_servicenames():
    """ Return the result of the following query:
    SELECT servicename FROM queue GROUP BY servicename ORDER BY servicename;
    """
    try:
        return Queue.query \
            .with_entities(Queue.servicename) \
            .group_by(Queue.servicename) \
            .order_by(Queue.servicename) \
            .all()
    except Exception as e:
        raise e


def db_queue_search(search):
    """ Given the search criteria, creates and executes the search query and
    returns the result set. The search parameter must be an associative array
    with each field to search and the correspondent value. Example:

    search = {
        'ts_after':    '2016-05-06 08:48:18',
        'hostname':    'myhost',
        'servicename': 'CPU',
        ...
    }
    """
    try:
        # Start by selecting only the fields we want to display
        # (to reduce the amount of data we transfer from the database)
        query = Queue.query \
            .with_entities(Queue.id, Queue.ts, Queue.source, Queue.eventid,
            Queue.lasteventid, Queue.type, Queue.state,
            Queue.count, Queue.handled, Queue.hostname,
            Queue.servicename, Queue.date, Queue.time,
            func.substr(Queue.message, 1, 30).label('message'))

        # Next build the where clause based on the search criteria...

        if search['tsdate_after']:
            if search['tstime_after']:
                # The Arrived After Time is only considered with the After Date
                query = query.filter(Queue.ts >= search['tsdate_after'] + ' ' + search['tstime_after'])
            else:
                # Otherwise assume *any* After Time
                query = query.filter(Queue.ts >= search['tsdate_after'])

        if search['tsdate_before']:
            if search['tstime_before']:
                # The Arrived Before Time is only considered with the Before Date
                query = query.filter(Queue.ts <= search['tsdate_before'] + ' ' + search['tstime_before'])
            else:
                # Otherwise assume *any* After Date
                query = query.filter(Queue.ts <= search['tsdate_before'])

        if search['date_after']:
            query = query.filter(Queue.date >= search['date_after'])
        if search['time_after']:
            # Generated After Time is considered independently of the After Date
            query = query.filter(Queue.time >= search['time_after'])

        if search['date_before']:
            query = query.filter(Queue.date <= search['date_before'])
        if search['time_before']:
            # Generated Before Time is considered independently of the Before Date
            query = query.filter(Queue.time <= search['time_before'])

        if search['eventid']:
            query = query.filter(or_(
                Queue.eventid == search['eventid'],
                Queue.lasteventid == search['eventid']
            ))

        if search['source']:
            query = query.filter(Queue.source.like(search['source']))

        if search['hostname']:
            query = query.filter(Queue.hostname.like(search['hostname']))

        if search['servicename']:
            query = query.filter(Queue.servicename.like(search['servicename']))

        if search['message']:
            query = query.filter(Queue.message.like(search['message']))

        if search['type_state']:
            query = query.filter(or_(
                and_(Queue.type == t, Queue.state == s) for t, s in search['type_state']
            ))

        if search['handled']:
            query = query.filter(or_(Queue.handled == h for h in search['handled']))

        # Order by timestamp makes more sense than ID, cause there's a counter
        # field, thus older records (lower ID) might have a newer timestamp
        oder = Queue.ts.desc() if search['sort'] == 1 else Queue.ts
        query = query.order_by(oder)

        if search['limit'] > 0 and search['limit'] <= 10000:
            query = query.limit(search['limit'])
        else:
            # Even if no limit is provided, impose a limit of 100 rows
            query = query.limit(100)

        # Re-write the SQL statement to look "more human readable"
        sql = str(query.statement)
        pos = sql.find('FROM')
        sql = ("SELECT id, ts, source, eventid, lasteventid, type, state,"
            " count, handled, hostname, servicename, date, time,"
            " message %s;" % sql[pos:])

        return (sql, query.all())
    except Exception as e:
        raise e
