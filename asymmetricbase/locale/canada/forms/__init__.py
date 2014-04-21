# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

import re

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError
from django.forms.fields import Field, RegexField, Select
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

# Override default localeflavor
phone_digits_re = re.compile(r'^(?:1-?)?(\d{3})[-\.]?(\d{3})[-\.]?(\d{4})$')
	
VALID_POSTAL_CODE_RE = r'^([ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ])(\d[ABCEGHJKLMNPRSTVWXYZ]\d)$'
INVALID_POSTAL_CODE_CHARS_RE = r'[^ABCEGHJKLMNPRSTVWXYZ0-9]'
	
class CAPostalCodeField(Field):
	"""
	Canadian postal code field.
	
	Validates against known invalid characters: D, F, I, O, Q, U
	Additionally the first character cannot be Z or W.
	For more info see:
	http://www.canadapost.ca/tools/pg/manual/PGaddress-e.asp#1402170
	"""
	default_error_messages = {
		'invalid': _(u'Enter a postal code in the format XXX XXX.'),
	}

	
	def clean(self, value):
		super(CAPostalCodeField, self).clean(value)
		
		if value in EMPTY_VALUES:
			return u''
		
		# remove non valid characters
		value = re.sub(INVALID_POSTAL_CODE_CHARS_RE, '', value.upper())
		m = re.match(VALID_POSTAL_CODE_RE, value)
		
		if m != None:
			return u'%s %s' % (m.group(1), m.group(2))
		else:
			raise ValidationError(self.error_messages['invalid'])
	
	
	def widget_attrs(self, widget):
		w = ''
		if 'class' in widget.attrs:
			w = ' ' + widget.attrs['class']
		return { 'class' : w }

class CAPhoneNumberField(Field):
	"""Canadian phone number field."""
	default_error_messages = {
		'invalid': u'Phone numbers must be at least ten digits.',
	}
	
	def clean(self, value):
		"""Validate a phone number.
		"""
		super(CAPhoneNumberField, self).clean(value)
		if value in EMPTY_VALUES:
			return u''
		value = re.sub('(\(|\)|\s+)', '', smart_unicode(value))
		
		m = phone_digits_re.search(value)
		if m:
			return u'(%s) %s-%s' % (m.group(1), m.group(2), m.group(3))
		raise ValidationError(self.error_messages['invalid'])
	
	def widget_attrs(self, widget):
		w = ''
		if 'class' in widget.attrs:
			w = ' ' + widget.attrs['class']
		return { 'class' : w }
