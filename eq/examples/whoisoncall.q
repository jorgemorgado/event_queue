#!/usr/bin/q
#
# This script is provided as an example only.
#
## Author: Jorge Morgado <jorge (at) morgado (dot) ch>
#

number = q.whoisoncall()

if number:
    print "The current on-call phone number is " + number
else:
    print "No on-call phone number currently set"
