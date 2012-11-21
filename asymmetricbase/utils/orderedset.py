# # {{{ http://code.activestate.com/recipes/576694/ (r7)
import collections

__all__ = ['OrderedSet']

KEY, PREV, NEXT = range(3)

class OrderedSet(collections.MutableSet):
	
	def __init__(self, iterable = None):
		self.end = end = []
		end += [None, end, end]		 # sentinel node for doubly linked list
		self.map = {}				 # key --> [key, prev, next]
		if iterable is not None:
			self |= iterable
	
	def __len__(self):
		return len(self.map)
	
	def __contains__(self, key):
		return key in self.map
	
	def add(self, key):
		if key not in self.map:
			end = self.end
			curr = end[PREV]
			curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]
	
	def update(self, *others):
		for other in others:
			try:
				for item in other:
					self.add(item)
			except TypeError:
				self.add(other)
	
	def discard(self, key):
		if key in self.map:
			key, prev_item, next_item = self.map.pop(key)
			prev_item[NEXT] = next_item
			next_item[PREV] = prev_item
	
	def __iter__(self):
		end = self.end
		curr = end[NEXT]
		while curr is not end:
			yield curr[KEY]
			curr = curr[NEXT]
	
	def __reversed__(self):
		end = self.end
		curr = end[PREV]
		while curr is not end:
			yield curr[KEY]
			curr = curr[PREV]
	
	def pop(self, last = True):
		if not self:
			raise KeyError('set is empty')
		key = next(reversed(self)) if last else next(iter(self))
		self.discard(key)
		return key
	
	def __repr__(self):
		if not self:
			return '{}()'.format(self.__class__.__name__,)
		return '{}({!r})'.format(self.__class__.__name__, list(self))
	
	def __eq__(self, other):
		if isinstance(other, OrderedSet):
			return len(self) == len(other) and list(self) == list(other)
		return set(self) == set(other)
	
	def __del__(self):
		self.clear()					# remove circular references

if __name__ == '__main__':
	print(OrderedSet('abracadaba'))
	print(OrderedSet('simsalabim'))
# # end of http://code.activestate.com/recipes/576694/ }}}