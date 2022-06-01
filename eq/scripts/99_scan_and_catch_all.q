#!/usr/bin/q

number = q.whoisoncall()

# Go to the first unhandled event in the queue
q.first_unhandled()

# Send an SMS if the state is CRITICAL
# Send everything via e-mail
while q.event is not None:
    if q.event.state() == 'CRITICAL':
        if not q.sendsms(number):
            q.sendsms(number, proto=q.SMTP)

    q.sendmail()
    q.next()
