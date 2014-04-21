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

from django.db import transaction

class ModelInitializer(object):
	"""
		This is an alternative to django fixtures, for initializing a database for tests.
		Each subclass of ModelInitializer initializes a number of objects for a specific model.
		a list of initializer classes are provided at the top of each test case, and will
		be loaded on setUp
	"""
	
	# list of initializers that need to be installed before me
	requirements = []
	
	def initialize(self, obj_callback = None):
		
		self.initialized_objects = self.get_objects_to_initialize()
		
		for obj in self.initialized_objects:
			if obj_callback is not None:
				obj_callback(obj)
			obj.save()
	
	def get_objects_to_initialize(self):
		"Returns a list of objects to be initalized"
		return []
	
	def finalize(self):
		pass
	
	class Constants(object):
		"Any extra constants one needs come here, but in the subclass"
		pass

def install_initializers(initializer_classes):
	from collections import defaultdict
	
	initialized_instances = []
	
	# Map[initializer_class, InitializerClassState]
	state = defaultdict(lambda: InitializerClassState.NOT_INSTALLED)
	
	with transaction.commit_on_success():
		_install_initializers_aux(state, initialized_instances, initializer_classes)
	
	return initialized_instances

# private
def _install_initializers_aux(state, initialized_instances, initializer_classes):
	for initializer_class in initializer_classes:
		initializer_class_state = state[initializer_class]
		
		if initializer_class_state == InitializerClassState.INSTALLED:
			continue
		
		if initializer_class_state == InitializerClassState.IN_PROGRESS:
			raise ModelInitializerCycleException(initializer_class)
		
		state[initializer_class] = InitializerClassState.IN_PROGRESS
		_install_initializers_aux(state, initialized_instances, initializer_class.requirements)
		mi = initializer_class()
		mi.initialize()
		initialized_instances.append(mi)
		state[initializer_class] = InitializerClassState.INSTALLED

# private
class InitializerClassState(object):
	NOT_INSTALLED = 0
	IN_PROGRESS = 1
	INSTALLED = 2

class ModelInitializerCycleException(Exception):
	pass
