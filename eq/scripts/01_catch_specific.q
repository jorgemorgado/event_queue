#!/usr/bin/q
#
# Specific Event Queue processing - skipping all the further scripts!
#
# This needs to be before catch_recovery script in order to implement the
# logic before that would "catch" them. Also to send "recoveries" to proper
# recipients again.

number = q.whoisoncall()

# Go to the first unhandled event in the queue
q.first_unhandled()

while q.event is not None:
    # Production hosts, send SMS
    if (q.event.source() in ['prod-poller1', 'prod-poller2']):

        # If it's a change to/from CRITICAL (or DOWN on host checks) to any other state
        if (q.event.state()     in ['CRITICAL', 'DOWN']
        or  q.event.laststate() in ['CRITICAL', 'DOWN']):

            # If it's not a service that is never urgent and thus mail-only
            if not (q.event.servicename() in ['IGNORE1', 'IGNORE2', 'IGNORE3']
            or      q.event.servicename().startswith('IGNORE4_')
            or      q.event.servicename().startswith('IGNORE5_')
            or      q.event.servicename().startswith('IGNORE6_')):
                if not q.sendsms(number):
                    q.sendsms(number, proto=q.SMTP)

            # In any case, also send an email to relevant people
            q.sendmail(['on-call@your.domain.com', 'user1@your-domain.com'])

    # Pre-production hosts, send email only
    elif (q.event.source() in ['prep-poller3', 'prep-poller4']):
        q.sendmail(['on-call@your.domain.com'])

    q.next()
