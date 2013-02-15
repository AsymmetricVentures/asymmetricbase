from collections import OrderedDict
from copy import deepcopy

from django.views.generic.base import View
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlencode
from django.template.response import ContentNotRenderedError

from asymmetricbase.views.mixins.multi_format_response import MultiFormatResponseMixin
from asymmetricbase.utils.exceptions import DeveloperTODO, ForceRollback
from asymmetricbase.logging import logger #@UnusedImport
from asymmetricbase.jinja import jinja_env
from asymmetricbase.utils.permissions import create_codename, \
	default_content_type_appname


class AsymBaseView(MultiFormatResponseMixin, View):
	""" Base class for all views """
	login_required = True
	permission_name = ''
	
	form_info = OrderedDict()
	
	def __init__(self, *args, **kwargs):
		self.forms = {}
		super(AsymBaseView, self).__init__(*args, **kwargs)
		self.successful = True
		self.forms = {}
	
	def preprocess(self, request, *args, **kwargs):
		"This is called before get or post are called. Used to prepare shared values"
		try:
			super(AsymBaseView, self).preprocess(request, *args, **kwargs)
		except AttributeError:
			pass
		try:
			super(AsymBaseView, self).mixin_preprocess(request, *args, **kwargs)
		except AttributeError:
			pass
	
	def predispatch(self, request, *args, **kwargs):
		""" Called after all preprocessing and form processing is done, but before get and post are called """
		try:
			super(AsymBaseView, self).predispatch(request, *args , **kwargs)
		except AttributeError:
			pass
	
	def load_forms(self, request):
		
		for form_name, form_data in self.forms.items():
			
			form_instance = form_data(request)
			
			setattr(self, form_name, form_instance)
			self.context[form_name] = form_instance
			
			form_data.process_callbacks()
	
	def get_form_data(self):
		self.forms = OrderedDict()
		# Create an instance copy of the form data
		forms = deepcopy(self._merge_attr('form_info'))
		
		# Now make sure they're in the correct order
		
		# First pass, just create the dependencies (update all parents)
		for form_name, form_data in forms.items():
			for child_name in form_data.children:
				forms[child_name].parents.update([form_name])
			
			for parent_name in form_data.parents:
				forms[parent_name].children.update([form_name])
		
		added = OrderedDict() # The forms we've already added
		top = OrderedDict() # The forms we're looking at
		new_top = OrderedDict() # The forms we'll look at next
		
		# Second pass, find forms with no dependencies
		for form_name, form_data in forms.items():
			if len(form_data.parents) == 0:
				top[form_name] = form_data
		
		while len(top):
			for form_name, form_data in top.items():
				if (form_name not in added) and (set(form_data.parents) <= set(added.keys())):
					for name in form_data.children: # can't rely on dict comprehensions being ordered
						new_top[name] = forms[name]
					added[form_name] = form_data
			
			top = new_top
			new_top = OrderedDict()
		
		# added should now contain the forms in an order that resolves
		# the dependencies, yet preserves the original insert order best it can
		
		self.forms = added
	
	def dispatch(self, request, *args, **kwargs):
		try:
			self.request = request
			logger.debug('BEGIN REQUEST *********** {}'.format(request.path))
			if not self._login_requirement_ok(request):
				logger.debug('Login requirement is not ok, redirecting')
				self.error('You were not logged in properly. Please try again')
				return redirect('{}?{}={}'.format(
					reverse(getattr(settings, 'ASYM_FAILED_LOGIN_URL')),
					REDIRECT_FIELD_NAME,
					request.path,
				))
			
			logger.debug(u'User is: {}'.format(request.user))
			permissions_required = self._merge_attr('permissions_required')
			
			logger.debug('The required permissions are {}'.format(permissions_required))
			
			if self.login_required:
				suffix = ''
				if hasattr(self, 'permission_name'):
					suffix = AsymBaseView.get_view_name_and_suffix(self.permission_name, **kwargs)[1]
				
				view_perm = '{}.{}'.format(default_content_type_appname(), create_codename(self.__class__.__module__, self.__class__.__name__, suffix))
				if not request.user.has_perm(view_perm):
						messages.error(request, 'You do not have permission to view that page')
						logger.debug('Failed permission check {}'.format(view_perm))
						return redirect(reverse(getattr(settings, 'ASYM_FAILED_LOGIN_URL')))
				
				logger.debug('Has view permission: {}'.format(view_perm))
			
			logger.debug('AsymBaseView: Getting form data')
			self.get_form_data()
			
			# Do any preprocessing, which should also fill out the arguments
			# for the forms
			logger.debug('AsymBaseView: Preprocess')
			self.preprocess(request, *args, **kwargs)
			
			# Create the form instances, and place into context
			logger.debug('AsymBaseView: LoadForms')
			self.load_forms(request)
			
			logger.debug("AsymBaseView: Predispatch")
			self.predispatch(request, *args, **kwargs)
			
			try:
				logger.debug('AsymBaseView: dispatch')
				response = super(AsymBaseView, self).dispatch(request, *args, **kwargs)
			except ForceRollback:
				# Ignore these because they're not real exceptions
				response = self.render_to_response()
			except ContentNotRenderedError as e:
				logger.exception(u"Content not rendered for template {}.".format(self.template_name))
				self.template_name = '500.djhtml'
				return self.render_to_response()
			
			logger.debug('END REQUEST*********')
			return response
		except DeveloperTODO as e:
			logger.error('{}'.format(e))
			self.template_name = 'todo_error.djhtml'
			return self.render_to_response()
		
	def get(self, request, *args, **kwargs):
		self.context['params'] = kwargs
		return self.render_to_response()
	
	def _login_requirement_ok(self, request):
		"Returns false if login is required and current user is not logged in"
		if not self.login_required:
			return True
		if request.user.is_authenticated():
			return True
		
		return False
	
	def has_permissions(self, perms, obj = None):
		return self.request.user.has_perms(perms, obj)
	
	def has_perm(self, perm, obj = None):
		return self.request.user.has_perm(perm, obj)
	
	def error(self, msg):
		messages.error(self.request, msg)
	
	def warning(self, msg):
		messages.warning(self.request, msg)
	
	def success(self, msg):
		messages.success(self.request, msg)
	
	def info(self, msg):
		messages.info(self.request, msg)
	
	def add_errors(self, error_list):
		error_messages = None
		# check if error_list is a dict or list of dicts
		if isinstance(error_list, dict):
			error_messages = { unicode(err) for error in error_list.values() for err in error }
		elif len(error_list) and isinstance(error_list[0], dict):
			error_messages = { unicode(e) for error in error_list for err in error.values() for e in err}
		else:
			error_messages = { unicode(error) for error in error_list }
		
		logger.debug('The following are add_errors()')
		for error in error_messages:
			if error.startswith('This field is required'):
				error = 'Required fields are marked with an asterisk'
			
			logger.debug('\t{}'.format(error))
			self.error(error)
	
	def enum(self, enum_class):
		""" Shortcut for adding enums to the context 
			>>> class MyEnum(Enum):
			...     P1 = 1
			...     P2 = 2
			...
			>>> # Shortcut for this:
			>>> self.context['MyEnum'] = MyEnum
		"""
		self.context[enum_class.__name__] = enum_class
	
	def get_rendered_template(self, request):
		return self.response_class(
			request = request,
			template = self.get_template_names(),
			context = self.context
		).rendered_content
	
	def get_rendered_macro(self, macro_name, template_name = None, **context):
		if template_name is None:
			template_name = self.get_template_names()
		
		template = jinja_env.get_template(template_name).module
		template_block = getattr(template, macro_name, None)
		
		if template_block is None:
			return ''
		
		return template_block(**context)
	
	@staticmethod
	def get_view_name_and_suffix(permission_name, **kwargs):
		suffix = ''
		name = ''
		
		if isinstance(permission_name, dict):
			for kwarg_key, kwarg_values in permission_name.items():
				kwarg_value = kwargs.get(kwarg_key, None)
				if kwarg_value in kwarg_values:
					data = kwarg_values[kwarg_value]
					name = data['name']
					suffix = data['codename']
					break
		
		return (name, suffix)
	
	@staticmethod
	def forbidden():
		return HttpResponseForbidden()
	
	@staticmethod
	def not_found():
		return HttpResponseNotFound()
	
	@staticmethod
	def redirect(to_string, *args, **kwargs):
		return redirect(to_string, *args, **kwargs)
	
	@staticmethod
	def reverse(*args, **kwargs):
		return reverse(*args, **kwargs)
	
	@staticmethod
	def resolve(*args, **kwargs):
		return resolve(*args, **kwargs)
	
	@staticmethod
	def urlencode(*args, **kwargs):
		return urlencode(*args, **kwargs)
	
	@staticmethod
	def commit_on_success():
		return transaction.commit_on_success()
