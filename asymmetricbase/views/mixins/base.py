
from asymmetricbase.logging import logger #@UnusedImport
from asymmetricbase.views.mixins.merge_attr import MergeAttrMixin

class AsymBaseMixin(MergeAttrMixin):
	def mixin_preprocess(self, request, *args, **kwargs):
		s = super(AsymBaseMixin, self)
		if hasattr(s, 'preprocess'):
			s.preprocess(request, *args, **kwargs)
