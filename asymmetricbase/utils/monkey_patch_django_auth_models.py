# -*- coding: utf-8 -*-
# Copyright (c) 2011, Steven Skoczen, GoodCloud, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification,are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer. Redistributions in binary 
# form must reproduce the above copyright notice, this list of conditions and 
# the following disclaimer in the documentation and/or other materials provided
# with the distribution.Neither the name of the GoodCloud, LLC. nor the names of
# its contributors may be used to endorse or promote products derived from this 
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Modified from:
# https://github.com/GoodCloud/django-longer-username/blob/master/longerusername/models.py
# Under BSD license.

from django.conf import settings
from django.db.models.signals import class_prepared
from django.core.validators import MaxLengthValidator

# Patch up Permission.name
MAX_PERMISSION_NAME_LENGTH = getattr(settings, 'MAX_PERMISSION_NAME_LENGTH', 128)
MAX_USERNAME_LENGTH = getattr(settings, 'MAX_USERNAME_LENGTH', 255)
MAX_EMAIL_LENGTH = getattr(settings, 'MAX_EMAIL_LENGTH', 254) # 254 chars == compliant with RFCs 3696 and 5321

def patch_model_field_length(model, field_name, max_length):
	field = model._meta.get_field(field_name)
	field.max_length = max_length
	
	for v in field.validators:
		if isinstance(v, MaxLengthValidator):
			v.limit_value = max_length

def patch_permission_model_signal(sender, *args, **kwargs):
	if sender.__module__ == 'django.contrib.auth.models':
		
		if sender.__name__ == 'Permission':
			patch_model_field_length(sender, 'name', MAX_PERMISSION_NAME_LENGTH)
		
		elif sender.__name__ == 'User':
			patch_model_field_length(sender, 'username', MAX_USERNAME_LENGTH)
			patch_model_field_length(sender, 'email', MAX_EMAIL_LENGTH)

class_prepared.connect(patch_permission_model_signal)

def monkey_patch():
	from django.contrib.auth.models import Permission, User
	
	is_permission_patched = Permission._meta.get_field('name').max_length >= MAX_PERMISSION_NAME_LENGTH #@UndefinedVariable
	is_user_patched = User._meta.get_field('username').max_length >= MAX_USERNAME_LENGTH #@UndefinedVariable
	is_user_patched = is_user_patched and User._meta.get_field('email').max_length >= MAX_EMAIL_LENGTH #@UndefinedVariable
	
	if not is_permission_patched:
		patch_permission_model_signal(Permission)
	
	if not is_user_patched:
		patch_permission_model_signal(User)
		

