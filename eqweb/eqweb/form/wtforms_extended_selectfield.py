#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# These classes are neeed because the WTForms does *not* yet support HTML
# select fields with 'optgroup' elements. It seems some future version should
# support this, so eventually these classes won't be needed (but the code will
# require some refactoring).
#
# From: https://github.com/industrydive/wtforms_extended_selectfield/blob/master/wtforms_extended_selectfield.py
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

from wtforms.fields import SelectField
from wtforms.validators import ValidationError
from wtforms.widgets import HTMLString, html_params
from cgi import escape
from wtforms.widgets import Select

# very loosely based on https://gist.github.com/playpauseandstop/1590178
__all__ = ('ExtendedSelectField', 'ExtendedSelectWidget')

__author__     = 'Eli Dickinson'
__copyright__  = 'Copyright (c)2013'
__credits__    = []
__license__    = 'unknown'
__version__    = '1.0.0'
__maintainer__ = 'Jorge Morgado'
__email__      = 'jorge (at) morgado (dot) ch'
__status__     = 'Production'

class ExtendedSelectWidget(Select):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for item1, item2 in field.choices:
            if isinstance(item2, (list,tuple)):
                group_label = item1
                group_items = item2
                html.append('<optgroup %s>' % html_params(label=group_label))
                for inner_val, inner_label in group_items:
                    html.append(self.render_option(inner_val, inner_label, inner_val == field.data))
                html.append('</optgroup>')
            else:
                val = item1
                label = item2
                html.append(self.render_option(val, label, val == field.data))
        html.append('</select>')
        return HTMLString(''.join(html))

class ExtendedSelectField(SelectField):
    """
    Add support of ``optgroup`` grouping to default WTForms' ``SelectField`` class.
    Here is an example of how the data is laid out.
        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            )),
            ('other','None Of The Above')
        )
    It's a little strange that the tuples are (value, label) except for groups which are (Group Label, list of tuples)
    but this is actually how Django does it too https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    widget = ExtendedSelectWidget()

    def pre_validate(self, form):
        """
        Don't forget to validate also values from embedded lists.
        """
        for item1,item2 in self.choices:
            if isinstance(item2, (list, tuple)):
                group_label = item1
                group_items = item2
                for val,label in group_items:
                    if val == self.data:
                        return
            else:
                val = item1
                label = item2
                if val == self.data:
                    return
        raise ValueError(self.gettext('Not a valid choice!'))
