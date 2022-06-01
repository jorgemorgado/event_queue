#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Several "generic" functions that don't fit anywhere else.
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

from flask import session, flash, Response


def get_sid():
    """ Return the session ID or None on error. """
    try:
        return session['username']
    except KeyError:
        return None


def unescape(s):
    """ Undo the HTML escape on a string - the opposite funtion of
    cgi.escape() which is not available on the cgi library.
    """
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    # This has to be last:
    s = s.replace('&amp;', '&')
    return s


def flash_form_errors(form):
    """ Flash the list of errors from form. """
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def get_typeahead(data):
    try:
        # Raise a 'no data' exception which will be caugth below
        if len(data) == 0: raise Exception('No data')

        res = []
        # Can't use this short form cause this won't catch row[0] == None
        # res = ['"' + row[0] + '"' for row in data]
        for row in data:
            if row[0] != None:
                res.append('"' + row[0] + '"')

        return Response('[' + ','.join(res) + ']', mimetype='application/json')

        # Add these headers to prevent the browser from caching the response
        # (use only if cache is a problem)
        # response.headers.add('Pragma', 'no-cache')
        # response.headers.add('Cache-Control', 'no-cache')
        # response.headers.add('Expires', 0)
        # return response
    except Exception as e:
        return Response('[]', mimetype='application/json')
