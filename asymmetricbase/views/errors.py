from asymmetricbase.views.base import AsymBaseView

class NotFoundView(AsymBaseView):
	template_name = '404.djhtml'

class ServerErrorView(AsymBaseView):
	template_name = '500.djhtml'
