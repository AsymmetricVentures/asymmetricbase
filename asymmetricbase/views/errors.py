from asymmetricbase.views.base import AsymBaseView

class PermissionDeniedView(AsymBaseView):
	template_name = '403.djhtml'

class NotFoundView(AsymBaseView):
	template_name = '404.djhtml'

class ServerErrorView(AsymBaseView):
	template_name = '500.djhtml'
