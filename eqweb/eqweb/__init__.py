#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Event Queue WebUI.
#
# Third party frameworks and extensions used in this application:
#
#  Server side:
#  * Flask web framework (http://flask.pocoo.org/)
#  * Flask Paginate (https://pythonhosted.org/Flask-paginate/)
#  * Flask SQLAlchemy (http://flask.pocoo.org/docs/latest/patterns/sqlalchemy/)
#  * SQLAlchemy toolkit (http://www.sqlalchemy.org/)
#  * Jinja2 templating engine (http://jinja.pocoo.org/docs/dev/)
#
#  Client side:
#  * Twitter's Bootstrap 3 (http://getbootstrap.com/)
#  * Bootstrap3 Typeahead (https://github.com/bassjobsen/Bootstrap-3-Typeahead)
#  * Bootstrap Multiselect (https://github.com/davidstutz/bootstrap-multiselect)
#  * Bootstrap3 Datepicker (https://eonasdan.github.io/bootstrap-datetimepicker)
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

import os
from flask import Flask, session, flash, render_template, redirect, request
from flask_paginate import Pagination

app = Flask(__name__)
app.config.from_pyfile('../eqweb.cfg')

# Sessions variables are stored client side - on the users browser the
# content of the variables is encrypted, so users can't actually see it.
# They could edit it, but again, as the content wouldn't be signed with
# this hash key, it wouldn't be valid.
# You need to set a secret key (random text) and keep it secret.
app.secret_key = app.config['SECRET_KEY']

from eqweb.db.db import *
from eqweb.utils.utils import *
from eqweb.form.login import LoginForm
from eqweb.form.search import SearchForm
from eqweb.form.signup import SignupForm


# ----------------------------------------------------------------------------
# JSON objects for type-ahead elements
# ----------------------------------------------------------------------------
@app.route('/source.json', methods=['GET'])
def source():
    return get_typeahead(db_queue_sources())

@app.route('/hostname.json', methods=['GET'])
def hostname():
    return get_typeahead(db_queue_hostnames())

@app.route('/servicename.json', methods=['GET'])
def servicename():
    return get_typeahead(db_queue_servicenames())


# ----------------------------------------------------------------------------
# Home page
# ----------------------------------------------------------------------------
@app.route('/')
def main():
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    data = None

    try:
        data = db.session.query(Query, User) \
            .join(User) \
            .with_entities(Query.id, Query.desc, Query.request, User.name, User.username) \
            .all()
    except Exception as e:
        flash(str(e))

    return render_template('index.html', page='home', sid=sid, data=data)


# ----------------------------------------------------------------------------
# Signup
# ----------------------------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Go to main page if *already* logged in
    sid = get_sid()
    if sid: return redirect('')

    form = None

    try:
        form = SignupForm(request.form)

        if request.method == 'POST':
            if form.validate():
                db.session.add(User(form.name.data, form.email.data, form.password.data))
                db.session.commit()

                session['username'] = form.email.data
                return redirect('')
            else:
                # If form didn't validate, flash the error(s)
                flash_form_errors(form)
    except IntegrityError:
        flash(u'User already exists.')
    except Exception as e:
        flash(str(e))

    return render_template('signup.html', page='signup', form=form)


# ----------------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Go to main page if *already* logged in
    sid = get_sid()
    if sid: return redirect('')

    form = None

    try:
        form = LoginForm(request.form)

        if request.method == 'POST':
            if form.validate():
                # Must have found exactly one row (user) and password must match
                user = User.query.filter_by(username=form.email.data).one()

                if user.check_password(form.password.data):
                    session['username'] = form.email.data
                    return redirect('')

                # If password check fails reports like the whole login failed
                raise NoResultFound
            else:
                # If form didn't validate, flash the error(s)
                flash_form_errors(form)
    except NoResultFound:
        flash(u'Wrong Email or Password.')
    except MultipleResultsFound:
        flash(u'This is embarrassing but your account seems to exist more than once. Please contact your Help Desk.')
    except Exception as e:
        flash(str(e))

    return render_template('login.html', page='login', form=form)


# ----------------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------------
@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
    except Exception as e:
        flash(str(e))

    return redirect('login')


# ----------------------------------------------------------------------------
# Save query
# ----------------------------------------------------------------------------
@app.route('/query_save', methods=['POST'])
def query_save():
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    try:
        if request and request.json:
            _name = request.json['name'].strip()
            _url = request.json['url'].strip()

            if _name and _url:
                _userid = db_get_userid(sid)

                if _userid:
                    # Save the query for this user
                    db.session.add(Query(_userid, _name, unescape(_url)))
                    db.session.commit()
    except Exception as e:
        # If we got here, it's silent error (print to log file but
        # the user won't receive any information about the problem)
        print "Error: %s" % str(e)

    # Return empty (204 No Content)
    return ('', 204)


# ----------------------------------------------------------------------------
# Edit query
# ----------------------------------------------------------------------------
@app.route('/query_edit', methods=['POST'])
def query_edit():
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    try:
        if request and request.json:
            _id = request.json['id']
            _desc = request.json['desc'].strip()

            if _id and _desc:
                _userid = db_get_userid(sid)

                if _userid:
                    query = Query.query.filter(and_(Query.id == _id, Query.userid == _userid)).one()
                    query.desc = _desc
                    db.session.commit()
    except Exception as e:
        # If we got here, it's silent error (print to log file but
        # the user won't receive any information about the problem)
        print "Error: %s" % str(e)

    # Return empty (204 No Content)
    return ('', 204)


# ----------------------------------------------------------------------------
# Delete query
# ----------------------------------------------------------------------------
@app.route('/query_delete', methods=['POST'])
def query_delete():
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    try:
        if request and request.json:
            _id = request.json['id']
            _userid = db_get_userid(sid)

            Query.query.filter(and_(Query.id == _id, Query.userid == _userid)).delete()
            db.session.commit()
    except Exception as e:
        # If we got here, it's silent error (print to log file but
        # the user won't receive any information about the problem)
        print "Error: %s" % str(e)

    # Return empty (204 No Content)
    return ('', 204)


# ----------------------------------------------------------------------------
# Event search
# ----------------------------------------------------------------------------
@app.route('/search', methods=['GET'])
def search():
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    form = None
    pagination = None
    data = None
    query = None
    page = None

    try:
        form = SearchForm(request.form)

        # Load the form's data from the get request
        form.set_data_from_get(request.args)

        # If there's a page in the request, remeber this for the results
        if request.args.get('page'): page = int(request.args.get('page'))

        if page or request.args.get('submit'):
            if form.validate():
                (query, data) = db_queue_search(form.get_search_criteria())
                count = len(data)

                if count == 0:
                    data = None
                    flash(u'No events found.')
                else:
                    if not page: page = 1

                    start = (page - 1) * app.config['PER_PAGE']
                    stop = start + app.config['PER_PAGE']
                    data = data[start:stop]

                    pagination = Pagination(
                        page = page,
                        found = count,
                        per_page = app.config['PER_PAGE'],
                        total = count,
                        record_name = 'events',
                        css_framework = app.config['CSS_FRAMEWORK'],
                        href = '?page={0}&' + form.get_search_url(),
                        search = True)
            else:
                # If form didn't validate, flash the error(s)
                flash_form_errors(form)
    except Exception as e:
        # print "Error (debug):", e
        # import traceback
        # traceback.print_exc()
        flash(str(e))

    return render_template('search.html',
        page='search',
        sid=sid,
        form=form,
        pagination=pagination,
        data=data,
        query=query)


# ----------------------------------------------------------------------------
# Event details
# ----------------------------------------------------------------------------
@app.route('/event', methods=['GET'], defaults = {'eventid': None})
@app.route('/event/<int:eventid>', methods=['GET'])
def event(eventid):
    # Go to login page if *not* logged in
    sid = get_sid()
    if not sid: return redirect('login')

    data = db_get_event(eventid) if eventid else None

    return render_template('event.html', page='event', data=data)


if __name__ == '__main__':
    app.run()
