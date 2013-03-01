import datetime
import os, warnings
import locale
from decimal import Decimal

from operator import attrgetter

from django.template.loaders.app_directories import fs_encoding, \
	app_template_dirs
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat, yesno, date as date_filter, urlencode
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.conf import settings

import jinja2
from jinja2.ext import WithExtension, LoopControlExtension
from jinja2.utils import contextfunction
from jinja2.runtime import Context
from jinja2.nodes import _context_function_types

from asymmetricbase.jinja.tags.csrf_token import CSRFTokenExtension
from asymmetricbase.jinja.tags.vtable import VTableExtension
from asymmetricbase.jinja.tags.haml import HamlishTagExtension
from asymmetricbase.jinja.tags.fielditerator import checkboxiterator, checkboxiterator_named, radioiterator, radioiterator_named


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
			def next(self): # @ReservedAssignment
				raise StopIteration()
			
		return EmptyIter()
		
	def __html__(self):
		return u'%NONE%'
	
	def __getattribute__(self, name, *args, **kwargs):
			
		try:
			return super(UndefinedVar, self).__getattribute__(name, *args, **kwargs)
		except AttributeError:
			if settings.TEMPLATE_DEBUG:
				import inspect
				f = inspect.currentframe().f_back.f_back.f_code
				file_name = f.co_filename
				lineno = f.co_firstlineno
				warnings.warn("[{}:{}] Trying to access attribute '{}' on undefined variable '{}'".format(file_name, lineno, name, self._undefined_name))
			return UndefinedVar()
		
		return None

def is_special_function(fn):
	return hasattr(fn, 'contextfunction') or hasattr(fn, 'evalcontextfunction') or hasattr(fn, 'environmentfunction')

def Context_call(__self, __obj, *args, **kwargs):
	"""Call the callable with the arguments and keyword arguments
	provided but inject the active context or environment as first
	argument if the callable is a :func:`contextfunction` or
	:func:`environmentfunction`.
	"""
	if __debug__:
		__traceback_hide__ = True
	
	if hasattr(__obj, '__call__') and is_special_function(__obj.__call__):
		__obj = getattr(__obj, '__call__')
		
	if isinstance(__obj, _context_function_types):
		if getattr(__obj, 'contextfunction', 0):
			args = (__self,) + args
		elif getattr(__obj, 'evalcontextfunction', 0):
			args = (__self.eval_ctx,) + args
		elif getattr(__obj, 'environmentfunction', 0):
			args = (__self.environment,) + args
	try:
		return __obj(*args, **kwargs)
	except StopIteration:
		return __self.environment.undefined('value was undefined because '
											'a callable raised a '
											'StopIteration exception')


template_loader = getattr(settings, 'ASYM_TEMPLATE_LOADER', jinja2.FileSystemLoader(app_template_dirs))
jinja_env = jinja2.Environment(
	loader = template_loader,
	undefined = UndefinedVar,
	autoescape = True,
	extensions = [
		CSRFTokenExtension,
		VTableExtension,
		HamlishTagExtension,
		WithExtension,
		LoopControlExtension
	]
)

def jinja_url(view_name, *args, **kwargs):
	return reverse(view_name, args = args, kwargs = kwargs)

def jinja_getdate():
	return timezone.localtime(timezone.now())

def jinja_date_filter(d, fmt = "%d/%b/%y %I:%M%p"):
	if not d:
		return ''
	return timezone.localtime(d).strftime(fmt)

def jinja_fmt(fmt, *args, **kwargs):
	return fmt.format(*args, **kwargs)

def jinja_getattr(obj, attr_string):
	"""
	Resolve attributes using jinja's getattr() rather than the default python method.
	
	Will also resolve chained attributes, for example:
	
		getattr(obj, 'user.name')
		
	will resolve obj.user.name
	"""
	if attr_string == '':
		return obj
	attrs = attr_string.split(".")
	for attr in attrs:
		obj = jinja_env.getattr(obj, attr)
	return obj

@contextfunction
def jinja_context_getattr(context, attr_string):
	"""
	Tries to get attribute by name from context
	"""
	return jinja_getattr(context, attr_string)

@contextfunction
def jinja_batch_context_getattr(context, *args, **kwargs):
	new_args = []
	new_kwargs = {}
	if args:
		for arg in args:
			new_args.append(jinja_context_getattr(context, arg))
		return new_args
	if kwargs:
		for k, v in kwargs.items():
			new_kwargs[k] = jinja_context_getattr(context, v)
		return new_kwargs

@contextfunction
def jinja_vtable(ctx, table, header = '', tail = ''):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml', globals = ctx).module.vtable(table, header, tail)

@contextfunction
def jinja_gridlayout(ctx, layout):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml', globals = ctx).module.gridlayout(layout)

@contextfunction
def jinja_display(ctx, layout):
	return jinja_env.get_template('asymmetricbase/displaymanager/base.djhtml', globals = ctx).module.display(layout)

def currency_format(num):
	if not isinstance(num, (int, float, long, Decimal)):
		num = 0
	return locale.currency(num, grouping = True)

jinja_env.globals.update({
	'url' : jinja_url,
	'getdatetime' : jinja_getdate,
	'type' : type,
	'dir' : dir,
	'getattr' : jinja_getattr,
	'context_getattr' : jinja_context_getattr,
	'batch_context_getattr' : jinja_batch_context_getattr,
	
	
	'vtable' : jinja_vtable,
	'gridlayout' : jinja_gridlayout,
	'display' : jinja_display,
})

jinja_env.filters.update({
	'date' : jinja_date_filter,
	'floatformat' : floatformat,
	'yesno' : yesno,
	'urlencode' : urlencode,
	'fmt' : jinja_fmt,
	'checkboxiterator' : checkboxiterator,
	'checkboxiterator_named' : checkboxiterator_named,
	'radioiterator' : radioiterator,
	'radioiterator_named' : radioiterator_named,
	'currency' : currency_format,
})

#jinja_env.compile_templates('/tmp/jinjatemplates', zip = None)

# Ugly hack to enable calling classes with @contextfunction
setattr(Context, 'call', Context_call)
