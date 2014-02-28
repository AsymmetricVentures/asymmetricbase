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

from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.http import urlquote
from django.conf import settings

from asymmetricbase.jinja.response import JinjaTemplateResponse
from asymmetricbase.views.mixins.merge_attr import MergeAttrMixin
from asymmetricbase.logging import logger # @UnusedImport
from asymmetricbase.utils.jsonencoder import AsymJSONEncoder, AsymJSTreeEncoder
from asymmetricbase.utils.resources import ResourceSet

class MultiFormatResponseMixin(MergeAttrMixin):
	""" A mixin that can be used to render a djhtml templates or return json data. """
	template_name = None
	output_type = 'html'
	response_class = JinjaTemplateResponse
	css_files = getattr(settings, 'ASYM_DEFAULT_CSS', ())
	js_files = getattr(settings, 'ASYM_DEFAULT_JS', ())
	
	def __init__(self):
		def dd(): return defaultdict(dd)
		
		self.context = dd()
	
	def get_context_data(self, **kwargs):
		css_files = self._merge_attr_signal('css_files', lambda x:  x.replace('scss', 'css'))
		css_resources = ResourceSet()
		css_resources.add(css_files)
		
		kwargs['css_files'] = css_resources 
		
		js_files = self._merge_attr_signal('js_files')
		js_resources = ResourceSet()
		js_resources.add(js_files)
		
		kwargs['js_files'] = js_resources
		
		return kwargs
	
	def render_to_response(self, **response_kwargs):
		""" Returns a response with a template rendered with the given context. """
		
		if self.output_type == 'html':
			
			self.context.update(self.get_context_data())
			return self.response_class(
				request = self.request,
				template = self.get_template_names(),
				context = self.context,
				**response_kwargs
			)
		
		else:
			encoder_table = {
				'json' : self._json_output,
				'jstree' : self._jstree_output,
				'pdf' : self._pdf_output,
				'other' : self._default_output,
			}
			
			encoder = encoder_table.get(self.output_type, 'other')
			response_kwargs = encoder()
			
			callback = response_kwargs.pop('__callback', None)
			
			response = HttpResponse(**response_kwargs)
			
			response['Content-Length'] = len(response_kwargs['content'])
			
			if callback is not None:
				# Add any extra headers to the response
				callback(response)
		
		
		if 'content_disposition' in self.context and self.context['content_disposition']:
			response['Content-Disposition'] = self.context['content_disposition']
		
		return response
	
	def _json_output(self):
		return {
			'content' : AsymJSONEncoder().encode(self.context),
			'content_type' : 'application/json'
		}
	
	def _jstree_output(self):
		return {
			'content' : AsymJSTreeEncoder().encode(self.context),
			'content_type' : 'application/json'
		}
	
	def _pdf_output(self):
		assert 'content_name' in self.context, "No name found in context['content_name']"
		
		ret_kwargs = self._default_output()
		ret_kwargs['content_type'] = 'application/pdf'
		
		return ret_kwargs
	
	def _default_output(self):
		assert 'content_data' in self.context, "Not data found in context['content_data']"
		
		ret_kwargs = {
			'content' : self.context['content_data'],
			'content_type' : self.context.get('content_type', None)
		}
		
		if 'content_name' in self.context:
			def callback(response):
				response['Content-Description'] = 'File Transfers'
				response['Content-Disposition'] = self.context.get('content_disposition', 'attachment; filename={}'.format(urlquote(self.context['content_name'])))
			
			ret_kwargs['__callback'] = callback
		return ret_kwargs
	
	def get_template_names(self):
		""" Returns a list of template names to be used for the request. Must return
			a list. May not be called if render_to_response is overridden. """
		if self.template_name is None:
			raise ImproperlyConfigured(
				"TemplateResponseMixin requires either a definition of "
				"'template_name' or an implementation of 'get_template_names()'")
		else:
			return [self.template_name]
