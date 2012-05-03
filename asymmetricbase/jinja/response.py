from django.template.response import TemplateResponse
from django.template.context import RequestContext

from asymmetricbase.jinja import jinja_env
from asymmetricbase.logging import logger #@UnusedImport

class JinjaTemplateResponse(TemplateResponse):
	
	def resolve_template(self, template):
		if isinstance(template, (list, tuple)):
			return jinja_env.select_template(template)
		elif isinstance(template, basestring):
			return jinja_env.get_template(template)
		else:
			return template
	
	def resolve_context(self, context):
		context = super(JinjaTemplateResponse, self).resolve_context(context)
		
		if isinstance(context, RequestContext):
			merged_context = {}
			for d in reversed(context.dicts):
				merged_context.update(d)
				
			context = merged_context
			
		return context
