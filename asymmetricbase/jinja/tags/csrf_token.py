from jinja2 import nodes
from jinja2.ext import Extension

from asymmetricbase.logging import logger #@UnusedImport

class CSRFTokenExtension(Extension):
	tags = set(['csrf_token'])
	
	def parse(self, parser):
		lineno = parser.stream.next().lineno
		
		return [
			nodes.Output([
				nodes.TemplateData('<input type="hidden" name="csrfmiddlewaretoken" value="'),
				nodes.Name('csrf_token', 'load'),
				nodes.TemplateData('" />'),
			]).set_lineno(lineno)
		]
