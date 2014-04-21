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

from django.test import TestCase
from django.test.testcases import assert_and_parse_html
from django.conf import settings

from asymmetricbase.views.mixins.merge_attr import MergeAttrMixin
from .model_initializer import install_initializers

class BaseTestCase(TestCase, MergeAttrMixin):
	"""Base class for all tests"""
	pre_initalizers = []
	
	def __init__(self, *args, **kwargs):
		super(BaseTestCase, self).__init__(*args, **kwargs)
		settings.IS_IN_TEST = True
	
	def __del__(self):
		"Hook method for deconstructing the class fixture after running all tests in the class."
		settings.IS_IN_TEST = False
	
	def _fixture_setup(self):
		super(BaseTestCase, self)._fixture_setup()
		
		all_initializers = self.pre_initalizers + self._get_inherited_initializers()
		
		self.initialized_instances = install_initializers(all_initializers)
	
	def _fixture_teardown(self):
		super(BaseTestCase, self)._fixture_teardown()
		for mi in self.initialized_instances:
			mi.finalize()
		self.initialized_instances = []
	
	def _get_inherited_initializers(self):
		"Returns a list of all initializers defined in this class and all its parents"
		return self._merge_attr('initializers').keys()
	
	def assertHTMLContains(self, html_content, html_substring, count = None, msg_prefix = ''):
		"""
		Asserts that a HTML string contains another HTML string
		"""
		
		if msg_prefix:
			msg_prefix += ": "
		
		content = assert_and_parse_html(self, unicode(html_content), None, u"Content is not valid HTML:")
		text = assert_and_parse_html(self, unicode(html_substring), None, u"Second argument is not valid HTML:")
		
		real_count = content.count(text)
		if count is not None:
			self.assertEqual(real_count, count, msg_prefix + "Found %d instances of '%s' in content (expected %d)" % (real_count, text, count))
		else:
			self.assertTrue(real_count != 0, msg_prefix + "Couldn't find '{}' in content '{}'".format(text, content))
