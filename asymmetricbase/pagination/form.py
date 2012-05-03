from asymmetricbase import forms
from asymmetricbase.logging import logger #@UnusedImport

class GetPaginationForm(forms.Form):
	page = forms.IntegerField(min_value = 0)
