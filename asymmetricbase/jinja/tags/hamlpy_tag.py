# -*- coding: utf-8 -*-
import re

from jinja2 import TemplateSyntaxError
from jinja2.ext import Extension

from hamlpy import hamlpy

from asymmetricbase.logging import logger  # @UnusedImport

begin_tag_rx = r'\{%\-?\s*haml.*?%\}'
end_tag_rx = r'\{%\-?\s*endhaml\s*\-?%\}'

begin_tag_m = re.compile(begin_tag_rx)
end_tag_m = re.compile(end_tag_rx)

class HamlpyExtension(Extension):
	tags = set(['haml'])
	
	def _get_lineno(self, source):
		matches = re.finditer(r"\n", source)
		if matches:
			return len(tuple(matches))
		return 0
	
	def parse(self, parser):
		# lineno = parser.stream.next().lineno
		haml_data = parser.parse_statements(['name:endhaml']) 
		parser.stream.expect('name:endhaml')
		return [
			haml_data
		]
	
	def preprocess(self, source, name, filename = None):
		ret_source = ''
		start_pos = 0
		
		h = hamlpy.Compiler()
		
		while True:
			tag_match = begin_tag_m.search(source, start_pos)
			
			if tag_match:
				
				end_tag = end_tag_m.search(source, tag_match.end())
				
				if not end_tag:
					raise TemplateSyntaxError('Expecting "endhaml" tag', self._get_lineno(source[:start_pos]))
				
				haml_source = source[tag_match.end() : end_tag.start()]
				
				try:
					ret_source += source[start_pos : tag_match.start()] + h.process(haml_source)
				except TemplateSyntaxError, e:
					raise TemplateSyntaxError(e.message, e.lineno, name = name, filename = filename)
				
				start_pos = end_tag.end()
			else:
				ret_source += source[start_pos:]
				break
			
		return ret_source