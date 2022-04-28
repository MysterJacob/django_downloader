from django.http import HttpResponse,FileResponse
from django.template import loader
from os import path
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
download_path = path.join(BASE_DIR, "downloads")

def index(request,file_name):
	new_path = path.join(download_path,file_name)
	try:
		f = open(str(new_path),"rb")
		return FileResponse(f)
	except FileNotFoundError:
		return HttpResponse("No such file")