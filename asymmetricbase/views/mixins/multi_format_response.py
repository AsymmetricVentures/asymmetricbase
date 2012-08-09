from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.http import urlquote
from django.conf import settings

from asymmetricbase.jinja.response import JinjaTemplateResponse
from asymmetricbase.views.mixins.merge_attr import MergeAttrMixin
from asymmetricbase.logging import logger #@UnusedImport
from asymmetricbase.utils.jsonencoder import AsymJSONEncoder
from asymmetricbase.utils.resources import ResourceSet
import os

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
	
	def render_to_response(self, **response_kwargs):
		""" Returns a response with a template rendered with the given context. """
		if self.output_type == 'html':
			css_files = self._merge_attr_signal('css_files', lambda x:  x.replace('scss', 'css'))
			css_resources = ResourceSet()
			css_resources.add(css_files)
			
			self.context['css_files'] = css_resources 
			
			js_files = self._merge_attr_signal('js_files')
			js_resources = ResourceSet()
			js_resources.add(js_files)
			
			self.context['js_files'] = js_resources
			
			return self.response_class(
				request = self.request,
				template = self.get_template_names(),
				context = self.context,
				**response_kwargs
			)
			
		elif self.output_type == 'json':
			json_str = AsymJSONEncoder().encode(self.context)
			return HttpResponse(json_str, mimetype = 'application/json')
		
		elif self.output_type == 'pdf':
			assert 'pdf_data' in self.context, 'PDF data not found in context["pdf_data"]'
			assert 'pdf_name' in self.context, 'PDF name not found in context["pdf_name"]'
			
			response = HttpResponse(self.context['pdf_data'], mimetype = 'application/pdf')
			response['Content-Description'] = 'File Transfers'
			response['Content-Length'] = len(self.context['pdf_data'])
			
			if hasattr(self, 'content_disposition') and self.content_disposition:
				response['Content-Disposition'] = self.content_disposition
			else:
				response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(self.context['pdf_name']))
			
			return response
		
		else:
			raise ImproperlyConfigured("Unknown output_type: {}".format(self.output_type))
	
	def get_template_names(self):
		""" Returns a list of template names to be used for the request. Must return
			a list. May not be called if render_to_response is overridden. """
		if self.template_name is None:
			raise ImproperlyConfigured(
				"TemplateResponseMixin requires either a definition of "
				"'template_name' or an implementation of 'get_template_names()'")
		else:
			return [self.template_name]
