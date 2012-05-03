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
