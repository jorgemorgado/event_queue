#!/usr/bin/q

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    if (q.event.servicename() == 'Puppet Agent'         # Services to catch
    or  q.event.servicename() == 'Puppet Run'):
        q.ignore()                                      # Ignore these

    q.next()
