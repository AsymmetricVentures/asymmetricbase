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

import re

from jinja2._markupsafe import Markup, escape

from asymmetricbase.logging import logger #@UnusedImport

def highlighter_wrapper(*queries):
	matchers = []
	
	for query in queries:
		if not query:
			continue
		rx = "({})".format(re.escape(query))
		matchers.append(re.compile(rx, re.I))
	
	def highlighter(phrase):
		phrase = unicode(phrase)
		for matcher in matchers:
			match = matcher.search(phrase)
			if match is not None:
				phrase = str(escape(phrase))
				phrase = Markup(matcher.sub(r"<strong>\1</strong>", phrase))
		return phrase
	return highlighter
