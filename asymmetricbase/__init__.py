from django.utils import html as django_html_utils

from jinja2._markupsafe import Markup

old_conditional_escape = django_html_utils.conditional_escape

def conditional_escape(html):
	"""
	Override django's conditional_escape to look for jinja's MarkupSafe
	"""
	if isinstance(html, Markup):
		return html
	else:
		return old_conditional_escape(html)
	
setattr(django_html_utils, 'conditional_escape', conditional_escape)
