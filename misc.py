import os
import json
import requests

def load_packages():
	with open('/var/cache/alps/packages.json') as fp:
		return sorted(json.load(fp), key = lambda i: i['name'])

def get_all_packages():
	url = 'https://flathub.org/api/v1/apps'
	r = requests.get(url = url)
	packages = r.json()
	return packages