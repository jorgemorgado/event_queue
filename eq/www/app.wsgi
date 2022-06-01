#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Implement a simple REST API for the event queue.
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# version 1.0
#

"""
Implements an API (a collection of routes) to the event queue database.

To run this under Apache, add the following configuration to your web-server,
and restart the service.

cat << EOF > /etc/apache2/conf.d/eq
<IfModule mod_wsgi.c>
    WSGIDaemonProcess eq user=www-data group=www-data processes=1 threads=5
    WSGIScriptAlias /eq /usr/local/q/www/app.wsgi

    <Directory /usr/local/q/www>
        WSGIProcessGroup eq
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</IfModule>
EOF
"""

import sys
import json
import datetime
import bottle
from bottle import route, request, abort

sys.path.append('../lib')
from dbevent.dbevent import DbEvent

def is_ipv4(addr):
    """ Validate an IPv4 address. """

    import socket
    try:
        socket.inet_aton(addr)  # Legal
        return True
    except socket.error:        # Not legal
        return False


def is_ipv6(addr):
    """ Valida an IPv6 address. """

    # FIXME Implement this function when IPv6 is needed.
    # FIXME For now, all IPv6 addresses are invalid!!
    return False


def save_event(event):
    """ Save the given event to the event queue. """

    try:
        db = DbEvent()
        _id = db.new_event(event['source'],
                           event['eventid'], event['lasteventid'],
                           event['type'],
                           event['state'], event['statetype'],
                           event['laststate'],
                           event['ipv4'], event['ipv6'],
                           event['hostname'], event['servicename'],
                           event['date'], event['time'],
                           event['message'])

        return str(_id)
    except Exception as e:
        abort(400, str(e))


def validate_event(event):
    """ Validate common event data. """

    if not event.has_key('source'):    abort(400, 'Missing event source.')
    if not event.has_key('type'):      abort(400, 'Missing notification type.')
    if not event.has_key('state'):     abort(400, 'Missing event state.')
    if not event.has_key('statetype'): abort(400, 'Missing event state-type.')
    # 'laststate' is optional so far, as not all Nagios will provide it
    if not event.has_key('laststate'): event['laststate'] = None
    if not event.has_key('hostname'):  abort(400, 'Missing hostname.')
    if not event.has_key('date'):      abort(400, 'Missing event date.')
    if not event.has_key('time'):      abort(400, 'Missing event time.')
    if not event.has_key('message'):   abort(400, 'Missing event message.')

    try:
        # Check if date is valid in the format DD-MM-YYYY
        oDate = datetime.datetime.strptime(event['date'], '%d-%m-%Y')
    except ValueError:
        try:
            # If we got here the above check failed, so check for YYYY-MM-DD
            oDate = datetime.datetime.strptime(event['date'], '%Y-%m-%d')
        except ValueError:
            abort(400, 'Invalid event date. Must be DD-MM-YYYY or YYYY-MM-DD.')
    else:
        # If we got here, it means the date is valid so invert its format
        event['date'] = oDate.strftime('%Y-%m-%d')

    try:
        datetime.datetime.strptime(event['time'], '%H:%M:%S')
    except ValueError:
        abort(400, 'Invalid event time. Must be HH:MM:SS.')

    return True


@route('/new-host-event', method='PUT')
def put_document():
    data = request.body.readline()
    if not data:
        abort(400, 'Missing host-event data.')

    event = json.loads(data)

    print("DEBUG EQ: new-host-event: %s" % data)

    if event.has_key('ipv4'):
        if not is_ipv4(event['ipv4']):
            abort(400, "Invalid IPv4 address (%s)." % event['ipv4'])
    else:
        event['ipv4'] = None

    if event.has_key('ipv6'):
        if not is_ipv6(event['ipv6']):
            abort(400, 'Invalid IPv6 address.')
    else:
        event['ipv6'] = None

    # Get the eventid and last eventid from the host (0 if not set)
    event['eventid'] = event['hosteventid'] \
        if event.has_key('hosteventid') else 0
    event['lasteventid'] = event['lasthosteventid'] \
        if event.has_key('lasthosteventid') else 0

    if validate_event(event):
        # There is no service name on host events
        event['servicename'] = None

        id = save_event(event)
        print("DEBUG EQ:  -> DB queue.id=%s" % id)


@route('/new-service-event', method='PUT')
def put_document():
    data = request.body.readline()
    if not data:
        abort(400, 'Missing service-event data.')

    event = json.loads(data)

    print("DEBUG EQ: new-service-event: %s" % data)

    if not event.has_key('servicename'):
        abort(400, 'Missing servicename.')

    # Get the eventid and last eventid from the service (0 if not set)
    event['eventid'] = event['serviceeventid'] \
        if event.has_key('serviceeventid') else 0
    event['lasteventid'] = event['lastserviceeventid'] \
        if event.has_key('lastserviceeventid') else 0

    if validate_event(event):
        # There are no IP addresses on service events
        event['ipv4'] = None
        event['ipv6'] = None

        id = save_event(event)
        print("DEBUG EQ:  -> DB queue.id=%s" % id)


@route('/new-heartbeat-event', method='PUT')
def put_document():
    data = request.body.readline()
    if not data:
        abort(400, 'Missing service-event data.')

    event = json.loads(data)

    # Validate heartbeat event data
    if not event.has_key('source'): abort(400, 'Missing event source.')
    if not event.has_key('type'):   abort(400, 'Missing event source.')
    if not event.has_key('state'):  abort(400, 'Missing event state.')
    if not event.has_key('date'):   abort(400, 'Missing event date.')
    if not event.has_key('time'):   abort(400, 'Missing event time.')
    if event['type'] != 'HEARTBEAT': abort(400, 'No heartbeat event found.')
    if event['state'] != 'ACTIVE':   abort(400, 'No active state found.')

    try:
        db = DbEvent()
        _id = db.new_heartbeat_event(event['source'],
                                     event['type'],
                                     event['state'],
                                     event['date'],
                                     event['time'])

        return str(_id)
    except Exception as e:
        abort(400, str(e))


#@route('/get-event/:id', method='GET')
#def get_document(id):
#    abort(404, 'No event with id %s' % id)
#    try:
#        db = DbEvent()
#        event = db.find_one({'_id':id})
#        if not event:
#            abort(404, 'No event with id %s' % id)
#    except Exception, e:
#        abort(400, str(e))


# Do NOT use bottle.run() with mod_wsgi
# bottle.run(host='localhost', port=8080)
bottle.run(host='localhost', port=8080, debug=True)

application = bottle.default_app()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
