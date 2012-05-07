from asymmetricbase.views.errors import PermissionDeniedView, NotFoundView, ServerErrorView

handler403 = PermissionDeniedView.as_view()
handler404 = NotFoundView.as_view()
handler500 = ServerErrorView.as_view()
