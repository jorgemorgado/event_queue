#!/usr/bin/q
#
# PLEASE KEEP THIS SCRIPT AT THE BEGINNING OF THE QUEUE SCANNING PROCESS.
#
# The goal of this script is to catch RECOVERY events as early as possible
# and ensure they are handled in the same way as the previous event which
# has generated this RECOVERY.
#
# For example, if there is a host DOWN or a service WARNING event, and such
# event is reported via email, once the RECOVERY happens, that should also
# be reported via email. Similarly, if a service CRITICAL event is reported
# via SMS, this script will ensure the RECOVERY will also be reported via SMS.
#

# Handled states (I mean, bits)
IGNORED  = 0   # 2^0 = 1
MAILSENT = 1   # 2^1 = 2
SMSSENT  = 2   # 2^2 = 4
#ETC...  = 3   # 2^3 = 8
#ETC...  = 4   # 2^4 = 16

# Go to the first unhandled event in the queue
q.first_unhandled()

number = q.whoisoncall()

while q.event is not None:
    if q.event.type() == 'RECOVERY':
        bits = q.find_last_event()

        if bits[IGNORED]:
            q.ignore()
        else:
            if bits[MAILSENT]:
                q.sendmail()
            if bits[SMSSENT]:
                q.sendsms(number)

    # Get the next event in the queue
    q.next()
