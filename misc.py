import os

def read_packages():
	with open('/var/cache/alps/packages.json') as fp:
		return json.load(fp)


	
