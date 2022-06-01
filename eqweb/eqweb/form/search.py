#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

"""
Event Queue WebUI search queue form.
"""

import os
from wtforms import Form, StringField, SelectField, IntegerField, SubmitField, DateField, DateTimeField, HiddenField, validators
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime

from wtforms_extended_selectfield import ExtendedSelectField

__author__     = 'Jorge Morgado'
__copyright__  = 'Copyright (c)2016'
__credits__    = []
__license__    = 'unknown'
__version__    = '1.0.0'
__maintainer__ = 'Jorge Morgado'
__email__      = 'jorge (at) morgado (dot) ch'
__status__     = 'Production'

class SearchForm(Form):
    tsdate_after  = DateField('arrived after date', format = '%Y-%m-%d', validators=[Optional()])
    tstime_after  = DateTimeField('arrived after time', format = '%H:%M:%S', validators=[Optional()])

    tsdate_before = DateField('arrived before date', format = '%Y-%m-%d', validators=[Optional()])
    tstime_before = DateTimeField('arrived before time', format = '%H:%M:%S', validators=[Optional()])

    date_after  = DateField('generated after date', format = '%Y-%m-%d', validators=[Optional()])
    time_after  = DateTimeField('generated after time', format = '%H:%M:%S', validators=[Optional()])

    date_before = DateField('generated before date', format = '%Y-%m-%d', validators=[Optional()])
    time_before = DateTimeField('generated before time', format = '%H:%M:%S', validators=[Optional()])

    source      = StringField('source', validators = [Length(min=0, max=255)])
    hostname    = StringField('hostname', validators = [Length(min=0, max=255)])
    servicename = StringField('service name', validators = [Length(min=0, max=255)])
    message     = StringField('message', validators = [Length(min=0, max=255)])

    eventid = IntegerField('event ID', validators=[Optional()])

    type_state = ExtendedSelectField('type and state', choices = [
        ('Problem',     [('0-0', 'Warning'), ('0-1', 'Critical'), ('0-2', 'Down'), ('0-3', 'Unknown')]),
        ('Recovery',    [('1-0', 'Ok'),      ('1-1', 'Up')]),
        ('Heartbeat',   [('2-0', 'Active'),  ('2-1', 'Inactive')]),
        ('Acknowledge', [('3-0', 'Warning'), ('3-1', 'Critical')]),
    ], validators=[Optional()])
    type_state_hidden = HiddenField('type_state_hidden')

    handled = SelectField('handled', choices = [
        ('0', 'Unhandled (0)'),
        ('1', 'Ignored (1)'),
        ('2', 'Mail (2)'),
        ('4', 'SMS (4)'),
        ('6', 'Mail and SMS (6)'),
    ], validators=[Optional()])
    handled_hidden = HiddenField('handled_hidden')

    limit = SelectField('limit', choices = [
        ('100', 'Top 100'),
        ('1000', 'Top 1\'000'),
        ('10000', 'Top 10\'000'),
        # ('0', 'All events (slower)'),
    ], default = '100')

    sort = SelectField('sort', choices = [
        ('1', 'Newer first (descending)'),
        ('2', 'Older first (ascending)'),
    ], default = '1')

    search_url = None

    submit = SubmitField('Search')
    reset = SubmitField('Reset')


    def __process_type_state(self):
        """ If no type/state options have been selected, return an empty
        array; otherwise, return an array of tuples with the selected event
        types and the correspondent event state.

        EVENT TYPE        | EVENT SUBTYPE (STATE)
        ------------------+-------------------------------------------------
        1 Problem         | 1-1 Warning, 1-2 Critical, 1-3 Down, 1-4 Unknown
        2 Recovery        | 2-1 Ok, 2-2 Up
        3 Heartbeat       | 3-1 Active, 3-2 Inactive
        4 Acknowledgement | 4-1 Warning, 4-2 Critical
        """
        types = ['PROBLEM', 'RECOVERY', 'HEARTBEAT', 'ACKNOWLEDGEMENT']
        states = {
            types[0]: ['WARNING', 'CRITICAL', 'DOWN', 'UNKNOWN'],
            types[1]: ['OK', 'UP'],
            types[2]: ['ACTIVE', 'INACTIVE'],
            types[3]: ['WARNING', 'CRITICAL'],
        }

        res = []
        if self.type_state_hidden.data and self.type_state_hidden.data != '':
            type_state = self.type_state_hidden.data.split(',')
            for item in type_state:
                t, s = item.split('-', 2)
                t = types[int(t)]
                s = states[t][int(s)]
                res.append((t, s))

        return res


    def __process_handled(self):
        """ If no handled options have been selected, return an empty array;
        otherwise, return an array with the selected handled values.
        """
        res = []
        if self.handled_hidden.data and self.handled_hidden.data != '':
            res = map(int, self.handled_hidden.data.split(','))

        return res


    def __process_date(self, value):
        return value.strftime('%Y-%m-%d') if value else None

    def __process_time(self, value):
        return value.strftime('%H:%M:%S') if value else None

    def __process_input(self, value):
        return None if value == '' else value

    def __process_number(self, value):
        return int(value) if value else None


    def validate(self):
        """ Override the validate method to add a few extra validations.
        """
        if not Form.validate(self): return False

        result = True

        if self.tsdate_after.data and self.tsdate_before.data:
            if self.tsdate_after.data > self.tsdate_before.data:
                self.tsdate_after.errors.append('After is higher than Before.')
                result = False

        if self.date_after.data and self.date_before.data:
            if self.date_after.data > self.date_before.data:
                self.date_after.errors.append('After is higher than Before.')
                result = False

        return result


    def get_search_criteria(self):
        """ Return an associative array with the search criteria.
        """
        return {
            'tsdate_after': self.__process_date(self.tsdate_after.data),
            'tstime_after': self.__process_time(self.tstime_after.data),

            'tsdate_before': self.__process_date(self.tsdate_before.data),
            'tstime_before': self.__process_time(self.tstime_before.data),

            'date_after': self.__process_date(self.date_after.data),
            'time_after': self.__process_time(self.time_after.data),

            'date_before': self.__process_date(self.date_before.data),
            'time_before': self.__process_time(self.time_before.data),

            'eventid': self.__process_number(self.eventid.data),

            'source':      self.__process_input(self.source.data),
            'hostname':    self.__process_input(self.hostname.data),
            'servicename': self.__process_input(self.servicename.data),
            'message':     self.__process_input(self.message.data),

            'type_state': self.__process_type_state(),
            'handled':    self.__process_handled(),

            'limit': int(self.limit.data),
            'sort':  int(self.sort.data),
        }


    def get_search_url(self):
        """ Return the search URL for an HTTP get query.

        It also keeps the search URL to be re-used if needed (i.e., when
        Save Query button is clicked we don't need to computhe the search
        URL again).
        """
        self.search_url = ''

        fields = [
            'eventid', 'source', 'type_state_hidden', 'handled_hidden',
            'hostname', 'servicename', 'message', 'limit', 'sort',
            'tsdate_after', 'tstime_after', 'tsdate_before', 'tstime_before',
            'date_after', 'time_after', 'date_before', 'time_before',
            ]

        for f in fields:
            if self[f].data:
                if f in ['tsdate_after', 'tsdate_before', 'date_after', 'date_before']:
                    self.search_url += "&%s=%s" % (f, self.__process_date(self[f].data))
                elif f in ['tstime_after', 'tstime_before', 'time_after', 'time_before']:
                    self.search_url += "&%s=%s" % (f, self.__process_time(self[f].data))
                else:
                    self.search_url += "&%s=%s" % (f, self[f].data)

        return self.search_url


    def set_data_from_get(self, request):
        """ Load the form's data from the a get request.

        Parameter 'request' is the request.args from the get request.
        """
        for f in ['eventid', 'source', 'hostname', 'servicename', 'message',
            'type_state_hidden', 'handled_hidden', 'limit', 'sort']:
            if request.get(f):
                self[f].data = request.get(f)
        for f in ['tsdate_after', 'tsdate_before', 'date_after', 'date_before']:
            if request.get(f):
                self[f].data = datetime.strptime(request.get(f), '%Y-%m-%d')
        for f in ['tstime_after', 'tstime_before', 'time_after', 'time_before']:
            if request.get(f):
                self[f].data = datetime.strptime(request.get(f), '%H:%M:%S')
