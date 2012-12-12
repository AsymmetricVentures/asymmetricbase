from asymmetricbase.views.base import AsymBaseView

class ErrorBaseView(AsymBaseView):
	@classmethod
	def as_view(cls, **initkwargs):
		v = super(AsymBaseView, cls).as_view(**initkwargs)
		
		def view(request, *args, **kwargs):
			response = v(request, *args, **kwargs)
			response.render()
			return response
		return view

class PermissionDeniedView(ErrorBaseView):
	template_name = '403.djhtml'

class NotFoundView(ErrorBaseView):
	template_name = '404.djhtml'

class ServerErrorView(ErrorBaseView):
	template_name = '500.djhtml'
