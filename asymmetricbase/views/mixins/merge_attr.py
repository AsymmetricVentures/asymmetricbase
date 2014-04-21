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

from collections import OrderedDict

from django.dispatch import Signal

from asymmetricbase.logging import logger #@UnusedImport

pre_merge = Signal(providing_args = ['instance', 'attr'])
post_merge = Signal(providing_args = ['instance', 'attr', 'merged'])

class MergeAttrMixin(object):
	@classmethod
	def _merge_attr(cls, attrname, process = None):
		attr_ret = OrderedDict()
		
		for base_class in cls.__bases__:
			if issubclass(base_class, MergeAttrMixin):
				attr_ret.update(base_class._merge_attr(attrname, process))
		
		if not hasattr(cls, attrname):
			return attr_ret
		
		new_attr = getattr(cls, attrname)
		
		if isinstance(new_attr, (list, tuple)):
			for item in new_attr:
				if item not in attr_ret:
					if process is not None:
						item = process(item)
						
					attr_ret[item] = True
					
		elif isinstance(new_attr, dict):
			for key, value in new_attr.items():
				if process is not None:
					value = process(value)
				
				attr_ret[key] = value
		
		return attr_ret
	
	def _merge_attr_signal(self, attrname, process = None):
		'''
		To use the signals:
		> def _post_merge(sender, **kwargs):
		>   instance = kwargs.pop('instance')
		>   attr = kwargs.pop('attr')
		>   merged = kwargs.pop('merged')
		>   if attr != 'css_files':
		>      return
		>   if instance.login_required and instance.request.user.is_authenticated():
		>     merged['loggedin.css'] = True
		> 
		> post_merge.connect(_post_merge)
		'''
		pre_merge.send(sender = self, instance = self, attr = attrname)
		ret = self._merge_attr(attrname, process)
		post_merge.send(sender = self, instance = self, attr = attrname, merged = ret)
		return ret
