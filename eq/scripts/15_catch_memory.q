#!/usr/bin/q

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    if (q.event.hostname() in ['prep-poller1', 'prep-poller2']  # Catch only those hosts
    and q.event.servicename() == 'Memory'):                     # Service to catch
        q.ignore()                                              # Ignore these

    q.next()
