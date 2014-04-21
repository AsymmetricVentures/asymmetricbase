# No license given
# Modified from: https://gist.github.com/972162/3230682034aefe517e0c08b4ff38a6c37509a0e9

from django.forms.forms import BaseForm
from django.forms.widgets import Media

import jinja2

from asymmetricbase.forms.boundfield import BoundField

def monkey_patch_django():
	"""
	Patching some django objects to make them "safe" for jinja's escape() function.
	Good for us it uses __html__() method.
	"""
	# Django's SafeString and SafeUnicode should not be escaped:
	from django.utils.safestring import SafeData
	SafeData.__html__ = lambda self: self
	
	from django.forms.formsets import BaseFormSet
	from django.forms.util import ErrorDict, ErrorList
	
	# If unicode returns SafeData, then escape will pass it outside unmodified thanks to patch above
	# If it's just a string it will be escaped
	for cls in (BaseForm, Media, BoundField, BaseFormSet, ErrorDict, ErrorList):
		cls.__html__ = lambda self: jinja2.escape(unicode(self))
