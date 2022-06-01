#!/usr/bin/q
#
# This script is provided as an example only.
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

import datetime

# Go to the first event in the queue
q.first()

while q.event is not None:

    date = q.event.date()

    try:
        oDate = datetime.datetime.strptime(date, '%d-%m-%Y')
        new_date = oDate.strftime('%Y-%m-%d')
        # print new_date

        q.db.db.update('queue',
            { 'date': "'" + new_date + "'", },
            { 'id': [ '%(id)s', q.event.id() ] })
    except ValueError:
        print "Date already in new format"

    # Get the next event in the queue
    q.next()
