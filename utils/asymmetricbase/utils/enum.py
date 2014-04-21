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

from collections import OrderedDict
from functools import total_ordering
import six

try:
	from itertools import zip_longest
except ImportError:
	from itertools import izip_longest as zip_longest

"""
Inspired by flufl.enum
"""

@total_ordering
class EnumItem(object):
	def __init__(self, **attrs):
		self.__dict__.update(**attrs)
		
	def __str__(self):
		return self.label
	
	def __int__(self):
		return self.value
	
	__long__ = __int__
	
	def __eq__(self, other):
		if isinstance(other, type(self)):
			return self.value == other.value
		return False
	
	def __hash__(self):
		return hash((type(self), self.label, self.value))
	
	def __lt__(self, other):
		if isinstance(other, type(self)):
			return self.value < other.value
		return False

class EnumMeta(type):
	
	def __new__(cls, name, bases, attributes):
		
		Choices = OrderedDict()
		new_attributes = {
			'reverse' : OrderedDict(),
			'__repr__' : lambda self: name,
		}
		items = {}
		
		meta = attributes.pop('Meta', {})
		properties = getattr(meta, 'properties', ('value', 'label'))
		
		if 'value' not in properties:
			properties = ('value',) + properties
		
		item_attrs = {
			'__repr__' : lambda self: '{}.{}'.format(name, self._enum_name_),
			'__reduce__' : lambda self: (self._enum_type_, (self.value,))
		}
		
		for k, v in attributes.items():
			# Enum values must be upper case
			if not k.isupper():
				# All instance methods get placed onto the enum values
				if callable(v) and getattr(v, 'im_self', None) is None and k != '__new__':
					item_attrs[k] = v
				else:
					new_attributes[k] = v
				continue
				
			item_type_attrs = {
				'label' : k.replace('_', ' ').title(),
				'display_order' : None,
				'_enum_name_' : k,
				'_enum_type_' : None
			}
			
			if not isinstance(v, tuple):
				v = (v,)
			
			if len(v) > len(properties):
				raise ValueError('Too many items for the properties')
			
			attr_updates = dict(zip_longest(properties, v))
			if attr_updates.get('label', -1) is None:
				attr_updates.pop('label')
			
			item_type_attrs.update(attr_updates)
			
			if item_type_attrs['value'] is None:
				raise ValueError('Enum values cannot be None')
			
			if not isinstance(item_type_attrs['value'], six.integer_types):
				raise TypeError('Enum ordinals must be integers')
			
			if item_type_attrs['display_order'] is None:
				item_type_attrs['display_order'] = item_type_attrs['value']
			
			items[k] = item_type_attrs
		
		ItemType = type(str('{}Item').format(name), (EnumItem,), item_attrs)
		
		for k, v in items.items():
			new_attributes[k] = ItemType(**v)
		
		sorted_items = sorted(items.values(), key = lambda x: x['display_order'])
		
		if len(items):
		
			for index, item in enumerate(sorted_items):
				new_attributes[item['_enum_name_']].display_order = item['display_order'] = index + 1
				Choices[item['value']] = item['label']
				new_attributes['reverse'][item['value']] = new_attributes[item['_enum_name_']]
			
		new_attributes['Choices'] = Choices
		EnumType = super(EnumMeta, cls).__new__(cls, name, bases, new_attributes)
		
		
		for item in EnumType:
			setattr(item, '_enum_type_', EnumType)
		
		return EnumType
	
	def __iter__(self):
		return iter(self.reverse.values())

def with_metaclass(meta, *bases):
	class metaclass(meta):
		__call__ = type.__call__
		__init__ = type.__init__
		def __new__(cls, name, this_bases, d):
			if this_bases is None:
				return type.__new__(cls, str(name), (), d)
			return meta(str(name), bases, d)
	return metaclass(str('temp'), None, {})

class Enum(with_metaclass(EnumMeta)):
	'''Baseclass for Enums. 
	   ** DO NOT define methods in here'''
	Choices = {}
	
	def __new__(cls, value):
		try:
			return cls.reverse[value]
		except KeyError:
			raise ValueError('{} has no "{}" value'.format(cls.__name__, value))

if __name__ == '__main__':
	class MyEnum(Enum):
		A = 1
		B = 2
	
	class MyEnum2(Enum):
		A = 1
		B = 2
	
	a1 = MyEnum.A
	b1 = MyEnum.B
	a2 = MyEnum2.A
	b2 = MyEnum2.B
	
	assert MyEnum.A._enum_type_ == MyEnum
	
	assert a1 == MyEnum.A
	assert a1 != MyEnum.B
	assert a1 != MyEnum2.A
	assert a1 != a2
	assert a1 is MyEnum.A
	assert isinstance(a1, EnumItem)
	assert not isinstance(a1, type(a2))
	assert isinstance(a1, type(a2).__bases__[0])
	
	assert MyEnum.A.display_order == 1
	
	class MyEnum3(Enum):
		class Meta(object):
			properties = ('label', 'value')
		
		A = 'Hello', 3
		B = 'Foo', 1
		
		def enum(self):
			return self.label
		
		@classmethod
		def getBLabel(cls):
			return cls.B.label
	
	assert str(MyEnum3.A) == 'Hello'
	assert str(MyEnum3.B) == 'Foo'
	assert MyEnum3.A != 3
	assert MyEnum3.A.enum() == 'Hello'
	assert MyEnum3.getBLabel() == 'Foo'
	try:
		MyEnum3.enum()
		assert False, 'MyEnum3.enum() exists'
	except AttributeError:
		pass
	
	assert MyEnum3.A > MyEnum3.B
	
	try:
		_ = MyEnum3.A > MyEnum.A
		assert False, 'Should not be able to compare MyEnum3.A > MyEnum.A'
	except:
		pass
	
	assert repr(MyEnum3.A) == 'MyEnum3.A'
	
	class MyEnum4(Enum):
		A = 1
		B = 3, 'Hello'
		UPPER_CASE_WORD = 4
	
	assert str(MyEnum4.A) == 'A'
	assert str(MyEnum4.B) == 'Hello'
	assert str(MyEnum4.UPPER_CASE_WORD) == 'Upper Case Word'
	
	assert MyEnum4(1) == MyEnum4.A
	assert MyEnum4(1) is MyEnum4.A
	
	try:
		MyEnum4(2)
		assert False, 'MyEnum4(2) Should fail.'
	except ValueError:
		pass
	
	assert MyEnum4(1).label == 'A'
	
	assert tuple(MyEnum4) == (MyEnum4.A, MyEnum4.B, MyEnum4.UPPER_CASE_WORD)
	
	assert MyEnum4.A in MyEnum4
	
	assert 1 not in MyEnum4
	if 1 in MyEnum4:
		assert False, 'Cannot test ints in Enums'
	
	try:
		class MyEnum5(Enum):
			A = 'a'
			B = 'b'
		assert False, 'Enum ordinals must be integers'
	except TypeError:
		pass
	
	class MyEnum6(Enum):
		A = 1, 2
		B = 2, 3
		C = 3, 1
		
		class Meta(object):
			properties = ('value', 'display_order')
	
	assert MyEnum6.A.display_order == 2
	assert tuple(MyEnum6) == (MyEnum6.C, MyEnum6.A, MyEnum6.B)
	
	# Enums should be hashable
	hash(MyEnum6.A)
	d = {MyEnum6.A : 'a'}
	assert d[MyEnum6.A] == 'a'
	
	import pickle
	
	d = pickle.dumps(MyEnum6.A, pickle.HIGHEST_PROTOCOL)
	r = pickle.loads(d)
	
	assert r == MyEnum6.A

