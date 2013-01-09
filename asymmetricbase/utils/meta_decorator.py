def meta(k,v):
	"""
	Decorator that adds value v at attribute k to the object being decorated.
	"""
	def dec(obj):
		setattr(obj, k, v)
		return obj
	return dec