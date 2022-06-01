#!/usr/bin/q
#
# This script is provided as an example only.
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

# Place the cursor on the first unhandled event
q.first_unhandled()

# Send the event to email
q.sendmail('your.email.address@your.domain.com')

# Or simply send to default email address
q.sendmail()
