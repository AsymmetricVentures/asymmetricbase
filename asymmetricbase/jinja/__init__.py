import datetime
import os, warnings

from django.template.loaders.app_directories import fs_encoding, \
	app_template_dirs
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat, yesno, date as date_filter
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.conf import settings

import jinja2
from jinja2.ext import WithExtension

from asymmetricbase.jinja.tags.csrf_token import CSRFTokenExtension
from asymmetricbase.jinja.tags.vtable import VTableExtension
from asymmetricbase.jinja.tags.haml import HamlishTagExtension, \
	HamlishExtension

class UndefinedVar(jinja2.Undefined):
	def __int__(self):
		return 0
	
	def __float__(self):
		return 0.0
	
	def __str__(self):
		return self.__html__()
	
	def __iter__(self):
		class EmptyIter(object):
			def __iter__(self):
				return self
			def next(self): #@ReservedAssignment
				raise StopIteration()
			
		return EmptyIter()
		
	def __html__(self):
		return u'%NONE%'
	
	def __getattribute__(self, name, *args, **kwargs):
			
		try:
			return super(UndefinedVar, self).__getattribute__(name, *args, **kwargs)
		except AttributeError:
			if settings.TEMPLATE_DEBUG:
				warnings.warn("Trying to access undefined attribute '{}.{}' on variable".format(self._undefined_name, name))
			return UndefinedVar()
		
		return None

jinja_env = jinja2.Environment(
	loader = jinja2.FileSystemLoader(app_template_dirs),
	undefined = UndefinedVar,
	autoescape = True,
	extensions = [
		CSRFTokenExtension,
		VTableExtension,
		HamlishExtension,
		HamlishTagExtension,
		WithExtension
	]
)

def jinja_url(view_name, *args, **kwargs):
	return reverse(view_name, args = args, kwargs = kwargs)

def jinja_getdate():
	return timezone.now()

def jinja_date_filter(d, fmt = "%d/%b/%y %I:%M%p"):
	return timezone.localtime(d).strftime(fmt)

jinja_env.globals.update({
	'url' : jinja_url,
	'getdatetime' : jinja_getdate,
})

jinja_env.filters.update({
	'date' : jinja_date_filter,
	'floatformat' : floatformat,
	'yesno' : yesno,
})
