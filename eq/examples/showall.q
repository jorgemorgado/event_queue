#!/usr/bin/q
#
# This script is provided as an example only.
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

# Go to the first event in the queue
q.first()

while q.event is not None:
    print "=" * 80
    print q.event

    # Get the next event in the queue
    q.next()
