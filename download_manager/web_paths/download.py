from django.http import HttpResponse
from django.template import loader
from threading import Thread
from pathlib import Path
from requests import get,head
from json import dumps,loads
from os import path
dw = {}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
download_path = path.join(BASE_DIR, "downloads")

def download_thread(url : str, token : str):

	bytes2mega = 1048576
	bytes2kilo = 1024
	# Get total size
	with head(url) as size_check:
		if size_check.ok:
			total_size = size_check.headers.get("content-length",0)
			dw[token]["total_size_mb"] = int(total_size) / bytes2mega

	chunk_size_kb = 1000 # 100 MB
	request = get(url,stream=True)
	pth = path.join(download_path,dw[token]["file_name"])
	with open(pth,"wb") as file:
		for chunk in request.iter_content(chunk_size= chunk_size_kb * bytes2kilo):
			file.write(chunk)
			file.flush()
			dw[token]["size_downloaded_mb"] += chunk_size_kb / bytes2kilo

			if dw[token]["canceled"] == True:
				break
			# print(dw)

			# dw[token]["size_downloaded_mb"] = min(dw[token]["size_downloaded_mb"],dw[token]["total_size_mb"])
	dw[token]["finished"] = True

 
def download(url : str, token : str):

	dt = Thread(target=download_thread,args=(url,token))

	dw[token] = {
		"url":url,
		"thread":dt,
		"size_downloaded_mb":0,
		"total_size_mb":0,
		"file_name":path.basename(url),
		"finished":False,
		"canceled":False
	}

	dt.start()
def render_info_page(token : str):
	template = loader.get_template("download.html")

	url = dw[token]["url"]
	file_name = dw[token]["file_name"]

	render = template.render(
			{"file_url":url,"token":token, "file_name":file_name},
	)
	return HttpResponse(render)

def start_downloading(url : str, token : str, request):
	template = loader.get_template("download.html")

	if url != None:
		download(url,token)
		return render_info_page(token)
	else:
		return HttpResponse("No file to download")

def cancel_download(request):
	token = request.GET.get("token",None)
	
	if token in dw:
		dw[token]["canceled"] = True

	return HttpResponse()

def status(request):
	token = request.GET.get("token",None)
	response = HttpResponse("",content_type="application/json")
	content = loads('{"error":false,"status":{}}')

	if token == None or not token in dw:
		response.status_code = 400
		content["error"] = True
	else:
		serialize = dw[token].copy()
		# print(serialize)
		del serialize["thread"]
		content["status"] = loads(dumps(serialize))

	response.content = dumps(content)
	return response 

def index(request):
	url_to_file = request.GET.get("file_url",None)
	token = request.GET.get("token","")
	if not token in dw:
		if url_to_file == None or url_to_file == "":
			return HttpResponse("INVALID URL")
		else:
			return start_downloading(url_to_file,token,request)
	else:
		return render_info_page(token)
	
