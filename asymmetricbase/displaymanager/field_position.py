
class FieldPosition(object): pass

class Before(FieldPosition):
	def __init__(self, target, field_type):
		self.target = target
		self.field_type = field_type

class After(FieldPosition):
	def __init__(self, target, field_type):
		self.target = target
		self.field_type = field_type

class Between(FieldPosition):
	def __init__(self, before, after, field_type):
		self.before = before
		self.after = after
		self.field_type = field_type
