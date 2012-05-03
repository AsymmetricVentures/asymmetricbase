from django.forms import widgets
from django.conf import settings

HTML5_WIDGETS = getattr(settings, 'ASYM_HTML5_WIDGETS',  {})

if HTML5_WIDGETS.get('time', False):
	widgets.TimeInput.input_type = 'time'
	
if HTML5_WIDGETS.get('date', False):
	widgets.DateInput.input_type = 'date'
	
if HTML5_WIDGETS.get('datetime', False):
	widgets.DateTimeInput.input_type = 'datetime'
