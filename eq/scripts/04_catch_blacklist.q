#!/usr/bin/q
#
# This should send mail to on-call when a mail server is blacklisted.
#

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    # Catch blacklist events and send mail ONLY!
    if (q.event.servicename() == 'SMTP Blacklist'):
        q.sendmail(['on-call@your.domain.com', 'user1@your-domain.com'])

    q.next()
