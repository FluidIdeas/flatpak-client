import os
import os.path
import json
import requests

def get_all_packages():
	if not os.path.exists('repository/all_packages.json'):
		url = 'https://flathub.org/api/v1/apps'
		r = requests.get(url = url, verify=True)
		packages = r.json()
		with open('repository/all_packages.json', 'w') as fp:
			json.dump(packages, fp)
	else:
		with open('repository/all_packages.json', 'r') as fp:
			packages = json.load(fp)
	return packages

def get_packages_by_category(category):
	if not os.path.exists('repository/' + category + '_packages.json'):
		url = 'https://flathub.org/api/v1/apps/category/'
		r = requests.get(url = url + category, verify=True)
		packages = r.json()
		with open('repository/' + category + '_packages.json', 'w') as fp:
			json.dump(packages, fp)
	else:
		with open('repository/' + category + '_packages.json', 'r') as fp:
			packages = json.load(fp)
	return packages

def get_package_details(package_id):
	url = 'https://flathub.org/api/v1/apps'
	r = requests.get(url = url + '/' + package_id, verify=True)
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