from django.http import HttpResponse
from django.template import loader
import secrets



def index(request):
	template = loader.get_template("index.html")
	render = template.render({"token":secrets.token_hex(32)},request)

	return HttpResponse(render)
