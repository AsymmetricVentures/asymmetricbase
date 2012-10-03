import re
import jinja2
from jinja2 import nodes
from jinja2.ext import Extension

from asymmetricbase.logging import logger #@UnusedImport

begin_tag_rx = r'\{%\-?\s*vtable_head.*?%\}'
begin_row_rx = r'\{%\-?\s*vtable_row\s*\-?%\}'
empty_rx = r'\{%\-?\s*empty\s*\-?%\}'
tail_rx = r'\{%\-?\s*vtable_tail\s*\-?%\}'
end_tag_rx = r'\{%\-?\s*endvtable\s*\-?%\}'

end_inner_cell_rx = r'^(.*?)(?:\]\]|$)'
pre_cell_rx = r'^(.*?)(?:\[\[)'
args_rx = r'^(?:\(([^\)]*)\))?(.*)$'

args_pat = re.compile(args_rx)
end_inner_cell_m = re.compile(end_inner_cell_rx)
pre_cell_m = re.compile(pre_cell_rx)
begin_tag_m = re.compile(begin_tag_rx)
begin_row_m = re.compile(begin_row_rx)
empty_m = re.compile(empty_rx)
tail_m = re.compile(tail_rx)
end_tag_m = re.compile(end_tag_rx)

import warnings
warnings.warn(
	'The Vtable tag will be deprecated in favour of the displaymanager module',
	DeprecationWarning
)

class VTableExtension(Extension):
	tags = set(['vtable'])
	
	def parse(self, parser):
		
		lineno = parser.stream.next().lineno
		
		table_name = parser.parse_expression()
		parser.stream.expect('name:for').lineno
		target = parser.parse_assign_target(extra_end_rules = ('name:in',))
		parser.stream.expect('name:in')
		for_iter = parser.parse_tuple(with_condexpr = False)
		
		pre_header = parser.parse_statements(['name:vtable_head'])
		parser.stream.expect('name:vtable_head')
		header = parser.parse_statements(['name:vtable_row'])
		parser.stream.expect('name:vtable_row')
		for_body = parser.parse_statements(['name:empty', 'name:vtable_tail'])
		
		if parser.stream.skip_if('name:empty'):
			empty = parser.parse_statements(['name:vtable_tail'])
		else:
			empty = []
		
		parser.stream.expect('name:vtable_tail')
		
		tail = parser.parse_statements(['name:endvtable'])
		parser.stream.expect('name:endvtable')
		
		# TODO: make this into a template
		return [
			nodes.Output([
				nodes.TemplateData('<div id="'),
				table_name,
				nodes.TemplateData('" class="vtable-container">\n'),
				nodes.TemplateData('<h3>'),
			])
		] + pre_header + [
			nodes.Output([
				nodes.TemplateData('</h3>\n'),
				nodes.TemplateData('<div class="vtable-rounded-container">\n'),
				nodes.TemplateData('<table class="vtable-table">\n'),
			]),
		] + header + [
			nodes.For(
				target, for_iter, for_body, empty, None, False, lineno = lineno
			),
			nodes.Output([
				nodes.TemplateData('</table>\n')
			])	
		] + tail + [
			nodes.Output([
				nodes.TemplateData('</div>\n</div>')
			])
		]
	
	def preprocess(self, source, name, filename = None):
		
		self.max_lines = len(filter(lambda x: x == '\n', source)) - 1
		ret_source = []
		
		tag_match = begin_tag_m.search(source)
		if  tag_match:
			last_end = 0
			
			while tag_match:
				header_start = tag_match.end()
				pre_header = source[last_end:header_start]
				row_match = begin_row_m.search(source, tag_match.end())
				
				if not row_match:
					lineno = self._get_lineno(pre_header)
					raise jinja2.TemplateSyntaxError("vtable_row tag not found", lineno)
				
				empty_match = empty_m.search(source, row_match.end())
				tail_match = tail_m.search(source, row_match.end())
				end_tag_match = end_tag_m.search(source, tail_match.end())
				
				if not all([empty_match, tail_match]):
					lineno = self._get_lineno(pre_header) + self._get_lineno(row_match.group(0))
					raise jinja2.TemplateSyntaxError("Expecting 'empty' tag or 'vtable_tail' tag", lineno)
				
				
				header_end = row_match.start()
				row_start = row_match.end()
				
				header_text = source[header_start:header_end]
				
				
				if empty_match:
					row_end = empty_match.start()
					empty_start = empty_match.end()
				else:
					row_end = tail_match.start()
					empty_start = tail_match.start()
				
				empty_end = tail_match.start()
				
				row_text = source[row_start:row_end]
				empty_text = source[empty_start:empty_end]
				tail_text = source[empty_end:end_tag_match.start()]
				
				self.lineno = self._get_lineno(pre_header)
				header_text = self.vtable_parse(header_text, is_header = True)
				self.lineno = self._get_lineno(pre_header) + self._get_lineno(header_text)
				row_text = self.vtable_parse(row_text, has_loop = True)
				self.lineno = self._get_lineno(pre_header) + self._get_lineno(header_text) + self._get_lineno(row_text)
				empty_text = self.vtable_parse(empty_text)
				self.lineno = self._get_lineno(pre_header) + self._get_lineno(header_text) + self._get_lineno(row_text) + self._get_lineno(empty_text)
				tail_text = self.vtable_parse(tail_text, is_header = True, in_table = False)
			
				last_end = end_tag_match.end()
			
				ret_source.append(
					pre_header + '\n' + 
					header_text + '\n' + 
					source[header_end:row_start] + '\n' + 
					row_text + '\n' + 
					source[row_end:empty_start] + '\n' + 
					empty_text + '\n' + 
					tail_text + '\n' + 
					source[end_tag_match.start():end_tag_match.end()]
				)
				
				tag_match = begin_tag_m.search(source, end_tag_match.end())
			
			ret_source.append(source[end_tag_match.end():])

			return '\n'.join(ret_source)
		
		else:
			return super(VTableExtension, self).preprocess(source, name, filename)
	
	def vtable_parse(self, source, is_header = False, has_loop = False, in_table = True):
		if not len(source):
			return ''
		
		self.cell_wrapper = "\n\t<th {}>\n\t\t{}\n\t</th>\n" if is_header else "\n\t<td {}>\n\t\t{}\n\t</td>\n"
		
		# Sanity check, make sure there are balanced [[ and ]]
		if self._count_lb(source) != self._count_rb(source):
			raise jinja2.TemplateSyntaxError("Unbalanced square brackets", self.lineno)
		
		# Sanity check, make sure there are balanced ( and )
		if self._count_lp(source) != self._count_rp(source):
			raise jinja2.TemplateSyntaxError("Unbalanced parenthesis", self.lineno)
		
		self._reset(has_loop)
		self.parse_string(source, in_table = in_table)
		return ''.join([s for s in self.ret_nodelist])
	
	def _reset(self, has_loop = True):
		self.in_node = False
		self.inner_nodelist = []
		if has_loop:
			self.ret_nodelist = [
				'\n<tr class="{{ loop.cycle("odd", "even") }}">\n\t\t'
			]
		else:
			self.ret_nodelist = [
				'\n\t<tr>\n\t\t'
			]
	
	def parse_string(self, text, in_table = True):
		self.lineno += self._get_lineno(text)
		s = text.replace('\n', '').replace('\r', '').strip()
		while len(s):
			if not self.in_node:
				if s.find('[[') == -1:
					# not a start node
					self.ret_nodelist.append(s)
					break
				else:
					# has a start node
					m = pre_cell_m.match(s)
					if m:
						# add the pre to node list
						self.ret_nodelist.append(m.group(1))
						
						self.in_node = True
						s = s[m.end():]
						s = self.parse_endtag(s)
					else:
						raise jinja2.TemplateSyntaxError("Should not get here. Node = '{}'".format(s), self.lineno)
			else:
				if s.find(']]') == -1:
					# Doesn't close the tag
					self.inner_nodelist.append(s)
					break
				else:
					# does close it
					s = self.parse_endtag(s)
		if in_table:
			self.ret_nodelist.append('\n</tr>\n')
	
	def parse_endtag(self, s):
		self.lineno += self._get_lineno(s)
		s = s.replace('\n', '').replace('\r', '')
		m = end_inner_cell_m.match(s)
		if m:
			contents = m.group(1)
			remaining = s[len(contents):]
			
			self.inner_nodelist.append(contents)
			
			if remaining.startswith(']]'):
				self.in_node = False
				
				remaining = remaining[2:]
				
				args_m = args_pat.search(remaining)
				if args_m:
					args_text = args_m.groups()[0] or ''
					remaining = args_m.groups()[1]
				else:
					args_text = ''
				
				self.ret_nodelist.append(self.new_cell(args_text))
			
			return remaining
		else:
			raise jinja2.TemplateSyntaxError('Should not get here. Node = "{}"'.format(s), self.lineno)
	
	def new_cell(self, args_text):
		args = self.parse_args(args_text)
		
		attrs = {
			'class' : args.get('class', '')
		}
		
		if 'span' in args:
			attrs['colspan'] = args['span']
		
		if 'align' in args:
			attrs['style'] = 'text-align: ' + args['align']
		
		cell_contents = ' '.join([s.strip() for s in self.inner_nodelist])
		attrs = ' '.join(['{}="{}"'.format(k, v) for k, v in attrs.items()])
		
		self.inner_nodelist = []
		
		return self.cell_wrapper.format(attrs, cell_contents)
	
	def parse_args(self, text):
		args = {}
		
		for pair in text.split(','):
			kv = pair.strip().split('=')
			
			if len(kv) > 1:
				args[kv[0].strip()] = kv[1].strip()
			else:
				args[kv[0].strip()] = True
		
		return args
	
	def _get_lineno(self, source):
		return min(len(filter(lambda x: x == '\n', source)), self.max_lines)
	
	def _count_rb(self, source):
		return len(filter(lambda x: x == ']', source))
	
	def _count_lb(self, source):
		return len(filter(lambda x: x == '[', source))
	
	def _count_rp(self, source):
		return len(filter(lambda x: x == ')', source))
	
	def _count_lp(self, source):
		return len(filter(lambda x: x == '(', source))
