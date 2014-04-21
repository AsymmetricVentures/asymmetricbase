# No license given.
# Modified from:http://stackoverflow.com/questions/3151469/per-request-cache-in-django

from threading import currentThread
import time

from django.core.cache.backends.locmem import LocMemCache

_request_cache = {}
_installed_middleware = False

def get_request_cache():
	assert _installed_middleware, 'RequestCacheMiddleware not loaded'
	return _request_cache[currentThread()]

# LocMemCache is a threadsafe local memory cache
class RequestCache(LocMemCache):
	def __init__(self):
		name = 'locmemcache@%i' % hash(currentThread())
		params = dict()
		super(RequestCache, self).__init__(name, params)
	
	def add(self, key, value, timeout = None, version = None):
		key = self.make_key(key, version = version)
		self.validate_key(key)
		with self._lock.writer():
			exp = self._expire_info.get(key)
			if exp is None or exp <= time.time():
				try:
					self._set(key, value, timeout)
					return True
				except Exception:
					pass
			return False

	def get(self, key, default = None, version = None):
		key = self.make_key(key, version = version)
		self.validate_key(key)
		with self._lock.reader():
			exp = self._expire_info.get(key)
			if exp is None:
				return default
			elif exp > time.time():
				try:
					return self._cache[key]
				except Exception:
					return default
		with self._lock.writer():
			try:
				del self._cache[key]
				del self._expire_info[key]
			except KeyError:
				pass
			return default

	def _set(self, key, value, timeout = None):
		if len(self._cache) >= self._max_entries:
			self._cull()
		if timeout is None:
			timeout = self.default_timeout
		self._cache[key] = value
		self._expire_info[key] = time.time() + timeout

	def set(self, key, value, timeout = None, version = None):
		key = self.make_key(key, version = version)
		self.validate_key(key)
		with self._lock.writer():
			self._set(key, value, timeout)

	def incr(self, key, delta = 1, version = None):
		value = self.get(key, version = version)
		if value is None:
			raise ValueError("Key '%s' not found" % key)
		new_value = value + delta
		key = self.make_key(key, version = version)
		with self._lock.writer():
			self._cache[key] = new_value
		return new_value

	def has_key(self, key, version = None):
		key = self.make_key(key, version = version)
		self.validate_key(key)
		with self._lock.reader():
			exp = self._expire_info.get(key)
			if exp is None:
				return False
			elif exp > time.time():
				return True

		with self._lock.writer():
			try:
				del self._cache[key]
				del self._expire_info[key]
			except KeyError:
				pass
			return False

class RequestCacheMiddleware(object):
	def __init__(self):
		global _installed_middleware
		_installed_middleware = True

	def process_request(self, request):
		cache = _request_cache.get(currentThread()) or RequestCache()
		_request_cache[currentThread()] = cache

		cache.clear()
