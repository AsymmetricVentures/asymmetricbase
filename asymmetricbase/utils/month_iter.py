import sys
from django.utils import timezone

class MonthIter(object):
	def __init__(self, start_date, end_date = None, months = 1):
		self.start_date = start_date.replace(day = 1)
		self.end_date = timezone.today().replace(day = 1) if end_date is None else end_date.replace(day = 1)
		self.months = months
		self.current = self.start_date
		
	def __iter__(self):
		return self
	
	def __next__(self):
		if self.current <= self.end_date:
			ret = self.current
			carry, new_month = divmod(self.current.month - 1 + self.months, 12)
			new_month += 1
			self.current = self.current.replace(year = self.current.year + carry, month = new_month)
			return ret 
		else:
			raise StopIteration()
	

if sys.version_info < (3, 0):
	MonthIter.next = MonthIter.__next__
