from django.core.serializers.json import DjangoJSONEncoder


class AsymJSONEncoder(DjangoJSONEncoder):
	
	def default(self, o):
		
		if hasattr(o, '__json__'):
			return o.__json__(self.default)
		else:
			return super(AsymJSONEncoder, self).default(o)
