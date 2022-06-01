#!/usr/bin/q

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    if q.event.servicename() == 'Swap':
        q.ignore()

    q.next()
