#!/usr/bin/q

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    if (q.event.hostname() in ['switch1', 'switch2']    # Catch only those hosts
        and q.event.servicename() == 'Ping'):           # Service to catch
        q.sendmail()                                    # Mail only

    q.next()
