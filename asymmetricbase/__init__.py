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

from django.utils import html as django_html_utils

from jinja2._markupsafe import Markup

old_conditional_escape = django_html_utils.conditional_escape

def conditional_escape(html):
	"""
	Override django's conditional_escape to look for jinja's MarkupSafe
	"""
	if isinstance(html, Markup):
		return html
	else:
		return old_conditional_escape(html)
	
setattr(django_html_utils, 'conditional_escape', conditional_escape)
