import os
import json

def load_packages():
	with open('/var/cache/alps/packages.json') as fp:
		return sorted(json.load(fp), key = lambda i: i['name'])

