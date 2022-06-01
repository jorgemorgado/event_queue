#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

"""
Event Queue WebUI login form.
"""

from wtforms import Form, StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Length, Email

__author__     = 'Jorge Morgado'
__copyright__  = 'Copyright (c)2016'
__credits__    = []
__license__    = 'unknown'
__version__    = '1.0.0'
__maintainer__ = 'Jorge Morgado'
__email__      = 'jorge (at) morgado (dot) ch'
__status__     = 'Production'

class LoginForm(Form):
    email = StringField('email address', validators = [
        DataRequired(),
        Email(),
        Length(min=6, max=45),
    ])
    password = PasswordField('password', validators = [
        DataRequired(),
        Length(min=10, max=50),
    ])

    submit = SubmitField('Login')
