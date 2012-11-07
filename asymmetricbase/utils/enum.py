from functools import total_ordering
from itertools import izip_longest
from collections import OrderedDict

"""
Inspired by flufl.enum
"""

@total_ordering
class EnumItem(object):
	def __init__(self, **attrs):
		self.__dict__.update(**attrs)
		
	def __str__(self):
		return self.label
	
	def __eq__(self, other):
		if isinstance(other, type(self)):
			return self.value == other.value
		return False
	
	def __lt__(self, other):
		if isinstance(other, type(self)):
			return self.value < other.value
		return False
	
class EnumMeta(type):
	def __new__(cls, name, bases, attributes):
		
		Choices = OrderedDict()
		new_attributes = {}
		enum_values = {}
		reverse_values = {}
		items = {}
		
		meta = attributes.pop('Meta', {})
		tuple_properties = getattr(meta, 'properties', ('value', 'label'))
		
		if 'value' not in tuple_properties:
			tuple_properties = ('value',) + tuple_properties
		
		item_attrs = {
			'__repr__' : lambda self: '{}.{}'.format(name, self._enum_name_)
		}
		
		
		for k, v in attributes.items():
			# Enum values must be upper case
			if not k.isupper():
				# All instance methods get placed onto the enum values
				if callable(v) and getattr(v, 'im_self', None) is None:
					item_attrs[k] = v
				else:
					new_attributes[k] = v
				continue
				
				
			item_type_attrs = {
				'label' : k.replace('_', ' ').title(),
				'_enum_name_' : k
			}
			
			if isinstance(v, tuple):
				if len(v) > len(tuple_properties):
					raise ValueError('Too many items for the properties')
				
				item_type_attrs.update(dict(izip_longest(tuple_properties, v)))
				
				if item_type_attrs['value'] is None:
					raise ValueError('Enum values cannot be None')
				
				
			
			elif isinstance(v, (int, basestring)):
				enum_values[k] = v
				reverse_values[v] = k
				item_type_attrs['value'] = v
			
			items[k] = item_type_attrs
		
		ItemType = type('{}Item'.format(name), (EnumItem,), item_attrs)
		
		for k, v in items.items():
			new_attributes[k] = ItemType(**v)
		
		for item in sorted(items.values(), key = lambda x: x['value']):
			Choices[item['value']] = item['label']
		
		new_attributes['Choices'] = Choices
		
		return super(EnumMeta, cls).__new__(cls, name, bases, new_attributes)

class Enum(object):
	__metaclass__ = EnumMeta
	Choices = {}
	
	
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
	
	assert a1 == MyEnum.A
	assert a1 != MyEnum.B
	assert a1 != MyEnum2.A
	assert a1 != a2
	assert a1 is MyEnum.A
	assert isinstance(a1, EnumItem)
	assert not isinstance(a1, type(a2))
	assert isinstance(a1, type(a2).__bases__[0])
	
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
	
	print MyEnum3.Choices[3]
