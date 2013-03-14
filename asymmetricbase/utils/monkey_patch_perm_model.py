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

def patch_permission_model(model):
	field = model._meta.get_field('name')
	field.max_length = MAX_PERMISSION_NAME_LENGTH
	
	for v in field.validators:
		if isinstance(v, MaxLengthValidator):
			v.limit_value = MAX_PERMISSION_NAME_LENGTH

def patch_permission_model_signal(sender, *args, **kwargs):
	if sender.__name__ == 'User' and sender.__module__ == 'django.contrib.auth.models':
		patch_permission_model(sender)

class_prepared.connect(patch_permission_model_signal)

def monkey_patch():
	from django.contrib.auth.models import Permission
	if Permission._meta.get_field('name').max_length != MAX_PERMISSION_NAME_LENGTH: #@UndefinedVariable
		patch_permission_model(Permission)

