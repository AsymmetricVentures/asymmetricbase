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

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

from asymmetricbase.forms.form_factory import FormFactory
from asymmetricbase.views.mixins.base import AsymBaseMixin

from .form import GetPaginationForm

class PaginationMixin(AsymBaseMixin):
	# Most, if not all, pages that use this mixin also have search
	js_files = ('search.controller.js',)
	form_info = OrderedDict(
		pagination_form = FormFactory(GetPaginationForm, use_GET = True),
	)
	
	def preprocess(self, request, *args, **kwargs):
		super(PaginationMixin, self).preprocess(request, *args, **kwargs)
		
		def get_pagination_callback(form, is_valid):
			self.page = 1
			
			if is_valid:
				self.page = form.cleaned_data['page']
		
		self.forms['pagination_form'].callbacks.append(get_pagination_callback)
		
		if not hasattr(self, 'results_per_page'):
			self.results_per_page = getattr(settings, 'ASYM_PAGINATION_DEFAULT_PAGES', 25)
	
	def _get_pagination_query(self, *args, **kwargs):
		raise NotImplementedError('Please override this in a baseclass')
	
	def get_pager(self, request, *args, **kwargs):
		"""
			search results are in get_pager().object_list
			pager is get_pager()
		"""
		queryset = self._get_pagination_query(request, *args, **kwargs)
		paginator = Paginator(queryset, self.results_per_page)
		page_items = []
		
		try:
			page_items = paginator.page(self.page)
		except (PageNotAnInteger, TypeError):
			page_items = paginator.page(1)
		except EmptyPage:
			page_items = paginator.page(paginator.num_pages)
		
		return page_items
		
	
