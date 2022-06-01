#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
#

"""
 This module implements several high-level functions for read/write access
to the event queue.
"""

import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from time import sleep
from subprocess import call

sys.path.append('../lib')
from dbevent.dbevent import DbEvent
from event.event import Event

__author__     = "Jorge Morgado"
__copyright__  = "Copyright (c)2014, Jorge Morgado"
__credits__    = []
__license__    = "unknown"
__version__    = "1.0.0"
__maintainer__ = "Jorge Morgado"
__email__      = "jorge (at) morgado (dot) ch"
__status__     = "Production"

class Q:
    'Common base class for the queue entity.'

    # TODO Set this from a configuration file
    # By default send emails to this address
    oncall_email_address = "eq-admin@your.domain.com"

    # TODO Set this from a configuration file
    # The relative path to the file that holds the on-call phone number
    oncall_phone_file = "../../var/set-oncall-phone"

    # The following protocols can be used when sending SMS
    SMPP = 1
    SMTP = 2


    def __init__(self):
        """ Initialize the queue for normal operations.
        """

        # The maximum timestamp value up to which events will be processed.
        # This should be provided as an argument to the q-script - if you are
        # processing several scripts at once, _always_ provide the same
        # date/time to ensure newer events (which might arrive after processing
        # has started) won't be processed. If not provided as an argument to
        # the q-script, takes the system's date/time when each script runs.
        self.ts_max = sys.argv[2] \
            if len(sys.argv) > 2 \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Open the database connection
        self.db = DbEvent()

        # At init time, there is no event set
        self.event = None


    def __del__(self):
        """ Finalize the queue.
        """

        # Destroy the database instance (and commit data)
        del self.db


    def age(self):
        """ Return the age of the event in seconds.
        """

        # The event's timestamp
        ts1 = self.event.ts()

        # The script's timestamp
        ts2 = datetime.strptime(self.ts_max, '%Y-%m-%d %H:%M:%S')

        # Return the difference between both
        return (ts2 - ts1).seconds


    def sleep(self, secs):
        """ Sleep for secs amount of seconds.
        """

        sleep(secs)


    def whoisoncall(self):
        """ Return the phone number of the current on-call or None if not found.
        """

        number = None

        # TODO realpath is not needed if the on-call phone number would be set
        # TODO from a configuration file (see class constructor)
        # Find the real and absolute path of this file
        realpath = os.path.dirname(os.path.realpath(__file__))
        phone_file = realpath + "/" + self.oncall_phone_file

        if os.path.exists(phone_file):
            f = open(phone_file, 'r')
            number = f.read()
            f.close()

        return number


    def ignore(self):
        """ Mark the current event as 'to be ignored'.
        """

        self.db.set_handled(self.event.id(), self.event.set_ignored())
        return True


    def sendmail(self, email=oncall_email_address):
        """ Send the current event to email.
        """

        # We expect a list of email addresses to notify, if we only get one as string, make it a sigle element list
        if not isinstance(email, list):
            email = [email]

        # Nothing to send if the cursor is not on a valid row
        if self.event is None:
            return False

        # Set some fields depending if this is a host or service event
        if not self.event.servicename():
            origin = 'HOST'
            subj = "%s on %s (state: %s) - Host" % \
                   (self.event.type(), self.event.hostname(), \
                   self.event.state())
            desc = "Host: %s (%s)" % \
                   (self.event.hostname(), self.event.ipv4())
        else:
            origin = 'SERVICE'
            subj = "%s on %s (state: %s) - Service '%s'" % \
                   (self.event.type(), self.event.hostname(), \
                   self.event.state(), self.event.servicename())
            desc = "Service: '%s' on %s" % \
                   (self.event.servicename(), self.event.hostname())

        # Create a text/plain message
        msg = MIMEText("**EQ %s event**\n\nType: %s\n%s\nState: %s\n" \
                       "Sent on: %s %s\nReceived on: %s\nSource: %s\n" \
                       "Event count: %d\n----\n%s" % \
                       (origin, self.event.type(), desc, self.event.state(), \
                        self.event.date(), self.event.time(), \
                        self.event.ts(), self.event.source(), \
                        self.event.count(), self.event.message()))
        msg['Subject'] = subj
        msg['From'] = self.oncall_email_address
        msg['To'] = ','.join(email)

        # Send message via local server, but don't include the envelope header
        s = smtplib.SMTP('localhost')
        s.sendmail(self.oncall_email_address, email, msg.as_string())
        s.quit()

        # Mark the event as 'mail has been sent'
        self.db.set_handled(self.event.id(), self.event.set_mailsent())

        # Sleep between emails to prevent hammering the remote gateway
        self.sleep(.25)

        return True


    def send_sms_via_smpp(self, number, message):
        """ Send the given message by SMS via SMPP.
        """

        ret = False

        # Send SMS via SMPP
        try:
            retcode = call([
                '/usr/local/q/bin/send-sms-smpp',
                '--destination', number,
                '--message', message
            ])

            if retcode < 0:
                self.send_sms_via_smtp(number, "SMS via SMPP failed. " \
                                    "Child exit code = %d\n\n" \
                                    "Message was:\n" \
                                    "%s" % (retcode, message))
            else:
                ret = True
        except OSError as e:
            message = ("Execution failed: ", e) + "\n\n" + message
            self.send_sms_via_smtp(number, "SMS via SMPP failed. " \
                                "Execution failed: %s\n\n" \
                                "Message was:\n" \
                                "%s" % (e, message))

        return ret


    def send_sms_via_smtp(self, number, message):
        """ Send the given message by SMS via SMTP.
        """

        rcpt = number + "@sms.your.gateway.com"

        # Create a text/plain message
        msg = MIMEText(message)

        msg['From'] = self.oncall_email_address
        msg['To'] = rcpt
        #msg['Subject'] = ''

        # Send message via local server, but don't include the envelope header
        s = smtplib.SMTP('localhost')
        s.sendmail(self.oncall_email_address, [rcpt], msg.as_string())
        s.quit()

        return True


    def sendsms(self, number, proto=SMPP):
        """ Send the current event to SMS via the specified protocol.
        """

        # Nothing to send if no number or the cursor is not on a valid row
        if number is None or self.event is None:
            return False

        # Set some fields depending if this is a host or service event
        if self.event.servicename():
            desc = "EQ Service '%s' on %s" % \
                   (self.event.servicename(), self.event.hostname())
        else:
            desc = "EQ Host %s" % \
                   (self.event.hostname())

        message = "%s/%s, %s. Info: %s. Time: %s %s" % \
                  (self.event.type(), self.event.state(),
                   desc, self.event.message(),
                   self.event.date(), self.event.time())

        # Mark the event as 'SMS has been sent'
        self.db.set_handled(self.event.id(), self.event.set_smssent())

        # Sleep between SMS to prevent hammering the remote gateway
        self.sleep(.25)

        if proto == self.SMTP:
            return self.send_sms_via_smtp(number, message)
        else:
            # By default, send SMS via SMPP
            return self.send_sms_via_smpp(number, message)


    def first(self):
        """ Set the cursor to the first event in the queue.
        """

        row = self.db.find_all(self.ts_max)
        self.event = None if row is None else Event(row)

        return self.event


    def first_heartbeat(self):
        """ Set the cursor to the first heartbeat events.
        """

        row = self.db.find_heartbeat(self.ts_max)
        self.event = None if row is None else Event(row)

        return self.event


    def first_unhandled(self):
        """ Set the cursor to the first unhandled event in the queue.
        """

        row = self.db.find_all_unhandled(self.ts_max)
        self.event = None if row is None else Event(row)

        return self.event


    def next(self):
        """ Set the cursor to the next event or None if no more events exits.
        """

        row = self.db.find_next()
        self.event = None if row is None else Event(row)

        return self.event


    def find_last_event(self):
        """ Given the current event, searches the queue for it's antecessor
            (i.e., the corresponding event that was generated before this one.
            It returns a tuple of booleans where each positions corresponds to
            the bits of the 'handled' field.
        """

        # Open a local database connection
        db = DbEvent()

        row = db.find_eventid(self.event.source(), self.event.lasteventid())

        if row is None:
            tup = (False, False, False)
        else:
            event = Event(row)
            tup = ( event.is_ignored(), event.is_mailsent(), event.is_smssent() )

        # Destroy the database instance (and commit data)
        del db

        return tup
