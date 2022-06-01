#!/bin/bash
#
# The service notification command is called by the poller and puts
# the notification to the Event Queue.
#
# This is just a wrapper to curl - it might be better to run curl
# directly from your Nagios poller. Although, if that fails to process
# the `hostname -s` (security reasons?) you can use this script (2-steps):
#
#       Nagios poller > (this script) > Event Queue
#
# Anyway, having an external script to push events to the EQ can be useful
# because it simplifies this taks. I.e., other tools can also use this script
# to push service notifications to the EQ (just make sure to respect the order
# of the arguments).
#
# Author: Jorge Morgado <jorge (at) morgado (dot) ch>
# Version: 1.0
#

HOSTNAME=`hostname -s`

# The JSON content
CONTENT=" \
  \"source\":\"${HOSTNAME}\", \
  \"type\":\"${1}\", \
  \"state\":\"${2}\", \
  \"statetype\":\"${3}\", \
  \"laststate\":\"${4}\", \
  \"hostname\":\"${5}\", \
  \"servicename\":\"${6}\", \
  \"date\":\"${7}\", \
  \"time\":\"${8}\", \
  \"message\":\"${9}\", \
  \"serviceeventid\":\"${10}\", \
  \"lastserviceeventid\":\"${11}\" \
"

/usr/bin/curl \
  -i \
  --noproxy eqhost \
  -H "Content-Type: application/json" \
  -X PUT \
  -d "{${CONTENT}}" \
  http://eqhost:5555/eq/new-service-event
