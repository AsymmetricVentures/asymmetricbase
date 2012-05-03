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
from jinja2.filters import evalcontextfilter
from jinja2._markupsafe import Markup
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
		return '%NONE%'
	
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
	return d.strftime(fmt)

def jinja_month(d):
	if isinstance(d, datetime.datetime):
		return d.strftime('%b')
	else:
		return datetime.date(2000, d, 1).strftime('%b')

def jinja_percent(d):
	return '{:.0f}'.format(d * 100)

@evalcontextfilter
def jinja_nl2br(ctx, text):
	result = unicode(text).replace('\n', '<br />')
	
	if ctx.autoescape:
		result = Markup(result)
	
	return result

@evalcontextfilter
def br2nl(ctx, value):
	result = unicode(value).replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
	
	if ctx.autoescape:
		result = Markup(result)
	return result

jinja_env.globals.update({
	'url' : jinja_url,
	'getdatetime' : jinja_getdate
})

jinja_env.filters.update({
	'date' : jinja_date_filter,
	'floatformat' : floatformat,
	'yesno' : yesno,
	'br2nl' : br2nl,
	'nl2br' : jinja_nl2br,
	
	'month' : jinja_month,
	'percent' : jinja_percent,
})
