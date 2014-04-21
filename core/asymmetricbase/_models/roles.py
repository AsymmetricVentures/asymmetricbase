# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals
from asymmetricbase.utils.cached_function import cached_function

__all__ = ('Role', 'AssignedRole', 'RoleTransfer', 'TypeAwareRoleManager', 'DefaultRole', 'OnlyRoleGroupProxy', 'HasTypeAwareRoleManager')

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import Group, GroupManager
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.conf import settings
from django.db import models

from asymmetricbase.logging import logger
from .base import AsymBaseModel
from asymmetricbase.fields import LongNameField

# UserModel implement get_groups_query_string()
# this method should return a string that can be used in a queryset
# filter to access the user's groups. For example, the default User class
# would return 'groups', since if we want to filter by groups we would
# do User.objecst.filter('groups__in' = foo)
UserModel = getattr(settings, 'ASYM_ROLE_USER_MODEL')
usermodel_related_fields = getattr(settings, 'ASYM_ROLE_USER_MODEL_SELECT_RELATED', None)

@cached_function
def get_user_role_model():
	''' Returns the model that the roles are attached to '''
	try:
		app_label, model_name = settings.ASYM_ROLE_USER_MODEL.split('.')
	except ValueError:
		raise ImproperlyConfigured("ASYM_ROLE_USER_MODEL must be of the form 'app_label.model_name'")
	
	user_model = models.get_model(app_label, model_name)
	if user_model is None:
		raise ImproperlyConfigured("ASYM_ROLE_USER_MODEL refers to model '{}' that has not been installed".format(settings.ASYM_ROLE_USER_MODEL))
	return user_model

class TypeAwareRoleManager(models.Manager):
	def __init__(self, model_content_type, *args, **kwargs):
		super(TypeAwareRoleManager, self).__init__(*args, **kwargs)
		self.model_content_type = model_content_type
	
	def get_queryset(self):
		return Role.objects.get_queryset() \
			.filter(defined_for = self.model_content_type)
	
	get_query_set = get_queryset

def HasTypeAwareRoleManager(content_type_model_name):
	""" If a model has a TypeAwareRoleManager (TARM) as a field, and its baseclass defines "objects",
	    then the TARM will override this as the default manager. In some cases this is not what is wanted,
	    if, for example, the primary key of the model is a CharField. In this case, the TARM causes an insert
	    to fail as it uses AutoField() instead of CharField() causing it to issue an int() on the field.
	"""
	attrs = {
		'assigned_roles' : generic.GenericRelation(AssignedRole),
		'roles' : property(lambda self: TypeAwareRoleManager(model_content_type = ContentType.objects.filter(model = content_type_model_name)))
	}
	
	return type(str('{}TypeAwareRoleManager'.format(content_type_model_name.title())), (object,), attrs)

class RoleGroupProxyManager(GroupManager):
	"""
	Manager that returns only the Group objects that either ARE or ARE NOT a permission_group
	for a Role object, depending on the parameter given at instantiation.
	"""
	
	def __init__(self, role_is_null, *args, **kwargs):
		self.role_is_null = role_is_null
		super(RoleGroupProxyManager, self).__init__(*args, **kwargs)
	
	def get_queryset(self):
		return Group.objects.filter(role__isnull = self.role_is_null)
	
	get_query_set = get_queryset

class NotRoleGroupProxy(Group):
	"""
	Proxy model to provide only those Group objects who are NOT a permission_group
	on a Role object.
	"""
	class Meta(object):
		proxy = True
	
	objects = RoleGroupProxyManager(role_is_null = True)

class OnlyRoleGroupProxy(Group):
	"""
	Proxy model to provide only those Group objects who ARE a permission_group
	on a Role object.
	"""
	class Meta(object):
		proxy = True
	
	objects = RoleGroupProxyManager(role_is_null = False)

class Role(AsymBaseModel):
	"""
	A Role is defined for a model class, and specifies a set of permissions,
	and a set of permitted groups, one of which a user must be in to be assigned this
	Role.
	
	Roles can be assigned to a User on a single object instance via AssignedRole.
	"""
	class Meta(object):
		unique_together = (
			('name', 'defined_for',),
		)
		app_label = 'shared'
	
	name = LongNameField()
	defined_for = models.ForeignKey(ContentType)
	# limit permitted groups to those groups that are not permission_groups for other Roles
	permitted_groups = models.ManyToManyField(Group, limit_choices_to = {'role__isnull' : True}, related_name = 'possible_roles')
	permission_group = models.OneToOneField(Group)
	
	def __str__(self):
		return "{} defined on {}".format(self.name, self.defined_for.model_class().__name__)
	
	@property
	def permitted_users(self):
		# looking at the .query for this QuerySet shows that you can, in fact,
		# do a .filter(set_of_things__in = another_set_of_things)
		user_role_model = get_user_role_model()
		queryset = user_role_model.objects.filter(**{user_role_model.get_groups_query_string() + '__id__in': self.permitted_groups.all()}).distinct()
		if usermodel_related_fields is not None:
			return queryset.select_related(*usermodel_related_fields)
		else:
			return queryset
		# the above is equivalent to:
#		users = set()
#		for g in self.permitted_groups.all():
#			for u in g.user_set.all():
#				users.add(u)
#		return users

class AssignedRole(AsymBaseModel):
	"""
	For adding Users in specific roles to models.
	"""
	user = models.ForeignKey(UserModel, related_name = 'assigned_roles')
	role = models.ForeignKey(Role, related_name = 'assignments')
	
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey()
	
	def __str__(self):
		return "Role '{}' on '{}'".format(self.role, self.content_type)
	
	def __copy__(self):
		return AssignedRole(
			user = self.user,
			role = self.role,
			content_object = self.content_object,
		)
	
	def save(self, *args, **kwargs):
		"""
		Check that role is defined on the content_type and user in permitted_groups.
		"""
		if self.role not in Role.objects.filter(defined_for = self.content_type):
			raise ValidationError("'{}' is not defined on '{}'".format(self.role, self.content_type))
		
		if self.user not in self.role.permitted_users:
			raise ValidationError("'{}' is not permitted to be assigned to '{}'".format(self.user, self.role))
		
		super(AssignedRole, self).save(*args, **kwargs)

class RoleTransfer(AsymBaseModel):
	role_from = models.ForeignKey(Role, related_name = '+')
	role_to = models.ForeignKey(Role, related_name = '+')
	
	def __html__(self):
		return "Transfer of {from.defined_for}.{from.name} to {to.defined_for}.{to.name}".format(**{'from' : self.role_from, 'to' : self.role_to})
	
	def __str__(self):
		return self.__html__()
	
	@classmethod
	def create(cls, from_model, to_model):
		"""
		`from_model` and `to_model` need to be instances of models.Model
		"""
		if type(from_model) == type(to_model):
			logger.info("Tried to create a role transfer on identical models {} and {}".format(from_model, to_model))
			return
		
		new_assigned_roles = []
		
		# All the transfers that could be made
		possible_transfers = cls.objects.filter(role_from__defined_for = from_model.get_content_type(), role_to__defined_for = to_model.get_content_type())
		
		for transfer in possible_transfers:
			# See if there are any assigned roles on the from_model
			assigned = AssignedRole.objects.filter(role = transfer.role_from, content_type = from_model.get_content_type(), object_id = from_model.id)
			
			# Now copy the role to the to_model
			for assigned_role in assigned:
				new_assigned_role, created = AssignedRole.objects.get_or_create(
					user = assigned_role.user,
					role = transfer.role_to,
					object_id = to_model.id,
					content_type = to_model.get_content_type()
				)
				
				logger.info("Created ({}) assigned role {}/{} for user {}".format(created, new_assigned_role, transfer, assigned_role.user))
				new_assigned_roles.append(new_assigned_role)
		
		return new_assigned_roles
	
	@classmethod
	def check_groups(cls, from_role, to_role):
		"""
		Check that all permitted groups in from_role are also present on to_role.
		Performing the transfer will fail if the groups are not present.
		
		Return a list of messages or None if no errors.
		"""
		msg_list = []
		for from_group in from_role.permitted_groups.all():
			if from_group not in to_role.permitted_groups.all():
				msg_list.append("""
				The {group} group is not a Permitted Group on the {role} role defined on {to_model}. The role transfer could fail if created.
				""".format(group = from_group.name, role = to_role.name, to_model = str(to_role.defined_for).title()))
		return msg_list if len(msg_list) > 0 else None

class DefaultRole(AsymBaseModel):
	"""
	Couple a static Role name defined in settings with a Role object.
	
	This allows renaming of the Roles while still being able to access it
	by name in the code.
	"""
	identifier = models.IntegerField(unique = True)
	role = models.ForeignKey(Role)
