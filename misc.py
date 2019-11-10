#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import os
import os.path
import json
import requests

def get_all_packages():
	if not os.path.exists('repository/all_packages.json'):
		url = 'https://flathub.org/api/v1/apps'
		r = requests.get(url = url, verify=True)
		packages = r.json()
		for p in packages:
			p['status'] = False
			if None != p['currentReleaseDate']:
				p['currentReleaseDate'] = p['currentReleaseDate'][:p['currentReleaseDate'].index('T')]
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

def create_menu_item(label, action_handler):
	item = Gtk.MenuItem.new_with_mnemonic(label)
	if action_handler != None:
		item.connect('activate', action_handler)
	return item

def create_menu(label, item_labels, action_handlers):
	menuitem = create_menu_item(label, None)
	menu = Gtk.Menu()
	for i in range(len(item_labels)):
		if item_labels[i] == '':
			item = Gtk.SeparatorMenuItem()
		else:
			item = create_menu_item(item_labels[i], action_handlers[i])
		menu.append(item)
	menuitem.set_submenu(menu)
	return menuitem

def create_main_menu(context):
	menubar = Gtk.MenuBar()
	menubar.append(create_menu('_Flatpak', ['_Refresh Apps', '_Update All Apps', '', '_Exit'], [
		context['menuActions']['refresh_apps'],
		context['menuActions']['update_all_apps'],
		None,
		context['menuActions']['exit']]))
	menubar.append(create_menu('_Apps', ['_Search', '', '_Install Selected', '_Update Selected', '', '_Uninstall Selected'], [
		context['menuActions']['search'],
		None,
		context['menuActions']['install_selected'],
		context['menuActions']['update_selected'],
		None,
		context['menuActions']['uninstall_selected']]))
	menubar.append(create_menu('_Settings', ['_Options'], [
		context['menuActions']['options']]))
	menubar.append(create_menu('_Help', ['_About'], [
		context['menuActions']['about']]))
	return menubar
