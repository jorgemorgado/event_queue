#!/usr/bin/q

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    if (q.event.hostname() == 'prep-poller1'    # Catch only those hosts
    and q.event.servicename() == 'CPU'):        # Service to catch
        q.ignore()                              # Ignore these

    q.next()
