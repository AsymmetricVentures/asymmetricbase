from collections import OrderedDict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

from asymmetricbase.logging import logger #@UnusedImport
from asymmetricbase.forms.form_factory import FormFactory
from asymmetricbase.pagination.form import GetPaginationForm
from asymmetricbase.views.mixins.base import AsymBaseMixin

class PaginationMixin(AsymBaseMixin):
	form_info = OrderedDict(
		pagination_form = FormFactory(GetPaginationForm, use_GET = True),
	)
	
	def preprocess(self, request, *args, **kwargs):
		super(PaginationMixin, self).preprocess(request, *args, **kwargs)
		
		def get_pagination_callback(form, is_valid):
			self.page = 1
			
			if is_valid:
				self.page = form.cleaned_data['page']
		
		self.forms['pagination_form'].callbacks.append(get_pagination_callback)
		
		if not hasattr(self, 'results_per_page'):
			self.results_per_page = getattr(settings, 'ASYM_PAGINATION_DEFAULT_PAGES',  25)
	
	def _get_pagination_query(self, *args, **kwargs):
		raise NotImplementedError('Please override this in a baseclass')
	
	def get_pager(self, request, *args, **kwargs):
		"""
			search results are in get_pager().object_list
			pager is get_pager()
		"""
		queryset = self._get_pagination_query(request, *args, **kwargs)
		paginator = Paginator(queryset, self.results_per_page)
		page_items = []
		
		try:
			page_items = paginator.page(self.page)
		except (PageNotAnInteger, TypeError):
			page_items = paginator.page(1)
		except EmptyPage:
			page_items = paginator.page(paginator.num_pages)
		
		return page_items
		
	
