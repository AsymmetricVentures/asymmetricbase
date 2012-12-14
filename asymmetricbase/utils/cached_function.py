from functools import wraps

def cached_function(func):
	"""
	Wrap a function so that it always returns the same thing, but only executes
	its code once.
	
	Similar to django's "cached_property"
	
	
	>>> def myfunc():
	...   print "HELLO"
	...   return 42
	>>> f = cached_function(myfunc)
	>>> myfunc()
	HELLO
	42
	>>> myfunc()
	HELLO
	42
	>>> f()
	HELLO
	42
	>>> f()
	42
	
	"""
	
	@wraps(func)
	def wrapper():
		if not hasattr(func, '__cached_result__'):
			func.__cached_result__ = func()
		
		return func.__cached_result__
	
	return wrapper
		

