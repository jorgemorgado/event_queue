#!/usr/bin/q
#
# This script is provided as an example only.
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    print "=" * 80
    print q.event

    # Could also mark the current even has handled so it won't bother us again
    #q.mark_as_handled()

    # Send current event via SMS (SMPP)
    #q.sendsms(q.whoisoncall())

    # Send current event via SMS SMTP
    #q.sendsms(q.whoisoncall(), q.SMTP)

    # Send current event via email
    #q.sendmail()

    # Get the next event in the queue
    q.next()
