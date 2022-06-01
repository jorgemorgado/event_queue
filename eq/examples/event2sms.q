#!/usr/bin/q
#
# This script is provided as an example only.
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

# Place the cursor on the first unhandled event
q.first_unhandled()

# Send the event to SMS (via SMTP protocol)
q.sendsms(number='+41xx1234567', proto=q.SMTP)

# Send an event to SMS (via default protocol)
q.sendsms(number='+41xx1234567')
