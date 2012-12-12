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
	
	def __int__(self):
		return self.value
	
	__long__ = __int__
	
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
		new_attributes = {
			'reverse'  : OrderedDict(),
			'__repr__' : name,
		}
		enum_values = []
		
		meta = attributes.pop('Meta', {})
		properties = getattr(meta, 'properties', ())
		
		if 'value' not in properties:
			properties = ('value',) + properties
		
		if 'label' not in properties:
			properties = properties + ('label',)
		
		if 'ordinal' not in properties:
			properties = properties + ('ordinal',)
		
		value_type_attrs = {
			'__repr__' : lambda self: '{}.{}'.format(name, self._enum_name_)
		}
		
		for k, v in attributes.items():
			# Enum values must be upper case
			if not k.isupper():
				# All instance methods get placed onto the enum values
				if callable(v) and getattr(v, 'im_self', None) is None and k != '__new__':
					value_type_attrs[k] = v
				else:
					new_attributes[k] = v
				continue
				
			enum_value_attrs = {
				'_enum_name_' : k,
				'_enum_type_' : None
			}
			
			if not isinstance(v, tuple):
				v = (v,)
			
			if len(v) > len(properties):
				raise ValueError("Too many items for the properties")
			
			enum_value_attrs.update(dict(izip_longest(properties, v)))
			
			if not enum_value_attrs.get('label'):
				enum_value_attrs['label'] = k.replace('_', ' ').title()
			
			if not isinstance(enum_value_attrs['value'], (int, long)):
				raise TypeError("Enum ordinals must be integers")
			
			if enum_value_attrs.get('ordinal') is None:
				enum_value_attrs['ordinal'] = enum_value_attrs['id']
			
			enum_values.append(enum_value_attrs)
		
		ValueType = type('{}Value'.format(name), (EnumItem,), value_type_attrs)
		enum_values = sorted(enum_values, key = lambda x: x['value'])
		
		for (index, enum_value_attrs) in enumerate(enum_values):
			enum_value_attrs['ordinal'] = index + 1
			enum_value = ValueType(**enum_value_attrs)
			
			new_attributes[enum_value_attrs['_enum_name_']] = enum_value
			new_attributes['reverse'][enum_value.value] = enum_value
		
		new_attributes['Choices'] = OrderedDict(
			(enum_value.value, enum_value.label)
			for enum_value in enum_values
		)
		
		EnumType = super(EnumMeta, cls).__new__(cls, name, bases, new_attributes)
		
		for enum_value in EnumType:
			setattr(enum_value, '_enum_type_', EnumType)
		
		return EnumType
	
	def __iter__(self):
		return iter(self.reverse.values())
	
class Enum(object):
	"""
		Baseclass for Enums. 
		** DO NOT define methods in here
	"""
	
	__metaclass__ = EnumMeta
	Choices = {}
	
	def __new__(cls, value):
		try:
			return cls.reverse[value]
		except KeyError:
			raise ValueError("{} has no value for '{}'".format(cls.__name__, value))

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
	
	class MyEnum3(Enum):
		class Meta(object):
			properties = ('label', 'value')
		
		A = "Hello", 3
		B = "Foo", 1
		
		def enum(self):
			return self.label
		
		@classmethod
		def getBLabel(cls):
			return cls.B.label
	
	assert str(MyEnum3.A) == "Hello"
	assert str(MyEnum3.B) == "Foo"
	assert MyEnum3.A != 3
	assert MyEnum3.A.enum() == "Hello"
	assert MyEnum3.getBLabel() == "Foo"
	try:
		MyEnum3.enum()
		assert False, "MyEnum3.enum() exists"
	except AttributeError:
		pass
	
	assert MyEnum3.A > MyEnum3.B
	
	try:
		_ = MyEnum3.A > MyEnum.A
		assert False, "Should not be able to compare MyEnum3.A > MyEnum.A"
	except:
		pass
	
	assert repr(MyEnum3.A) == 'MyEnum3.A'
	
	class MyEnum4(Enum):
		A = 1
		B = 3, "Hello"
		UPPER_CASE_WORD = 4
	
	assert str(MyEnum4.A) == "A"
	assert str(MyEnum4.B) == "Hello"
	assert str(MyEnum4.UPPER_CASE_WORD) == "Upper Case Word"
	
	assert MyEnum4(1) == MyEnum4.A
	assert MyEnum4(1) is MyEnum4.A
	
	try:
		MyEnum4(2)
		assert False, "MyEnum4(2) should fail."
	except ValueError:
		pass
	
	assert MyEnum4(1).label == "A"
	
	assert tuple(MyEnum4) == (MyEnum4.A, MyEnum4.B, MyEnum4.UPPER_CASE_WORD)
	
	assert MyEnum4.A in MyEnum4
	
	assert 1 not in MyEnum4
	if 1 in MyEnum4:
		assert False, "Cannot test ints in Enums"
	
	try:
		class MyEnum5(Enum):
			A = "a"
			B = "b"
		assert False, "Enum ordinals must be integers"
	except TypeError:
		pass
