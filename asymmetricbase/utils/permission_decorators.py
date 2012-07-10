from django.core.exceptions import PermissionDenied

def permissions_required(*permissions):
	def wrapper(view_func):
		def inner(self, request, *args, **kwargs):
			for perm in permissions:
				if not request.user.has_perm(perm):
					raise PermissionDenied
			return view_func(self, request, *args, **kwargs)
		return inner
	return wrapper
