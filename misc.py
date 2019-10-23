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

def get_packages_by_category(category):
	url = 'https://flathub.org/api/v1/apps/category/'
	r = requests.get(url = url + category)
	packages = r.json()
	return packages

def get_package_details(package_id):
	url = 'https://flathub.org/api/v1/apps'
	r = requests.get(url = url + '/' + package_id)
	package = r.json()
	return package

def download_package_database():
	packages = get_all_packages()
	database = dict()
	for i, package in enumerate(packages):
		print('Fetching ' + str(i) + ' of ' + str(len(packages)))
		details = get_package_details(package['flatpakAppId'])
		for category in details['categories']:
			if category['name'] not in database:
				database[category['name']] = list()
			database[category['name']].append(details)
	with open('flatpak-db.json', 'w') as fp:
		json.dump(database, fp, indent=4, sort_keys=True)
	return database