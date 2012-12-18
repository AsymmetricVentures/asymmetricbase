from django.db import models

from south.modelsinspector import add_introspection_rules

from asymmetricbase.logging import logger # @UnusedImport

'''
This file adds model fields for character fields of various lengths
'''

SHORT_MESSAGE_LENGTH = 140
LONG_MESSAGE_LENGTH = 255
SHORT_NAME_LENGTH = 50
LONG_NAME_LENGTH = (SHORT_MESSAGE_LENGTH * 2) + 5

COMMENT_LENGTH = 1024

class ShortMessageField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', SHORT_MESSAGE_LENGTH)
		super(ShortMessageField, self).__init__(*args, **kwargs)

class LongMessageField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', LONG_MESSAGE_LENGTH)
		super(LongMessageField, self).__init__(*args, **kwargs)

class ShortNameField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', SHORT_NAME_LENGTH)
		super(ShortNameField, self).__init__(*args, **kwargs)

class LongNameField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', LONG_NAME_LENGTH)
		super(LongNameField, self).__init__(*args, **kwargs)

class CommentField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('max_length', COMMENT_LENGTH)
		super(CommentField, self).__init__(*args, **kwargs)

add_introspection_rules([], [
	'^asymmetricbase\.fields\.textfields\.ShortMessageField',
	'^asymmetricbase\.fields\.textfields\.LongMessageField',
	'^asymmetricbase\.fields\.textfields\.ShortMessageField',
	'^asymmetricbase\.fields\.textfields\.LongMessageField',
	'^asymmetricbase\.fields\.textfields\.CommentField',
])
