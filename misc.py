#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk, GLib

import os
import os.path
import json
import requests
import threading
import time

def get_screen_size():
	display = Gdk.Display.get_default()
	monitor = display.get_primary_monitor()
	geometry = monitor.get_geometry()
	width = geometry.width
	height = geometry.height
	return (width, height)

def run_as_new_thread_with_progress(function, args, status_bar):
	thread = threading.Thread(target=function_with_progress, args=[function, args, status_bar])
	thread.daemon = True
	thread.start()

def function_with_progress(function, args, status_bar):
	GLib.timeout_add(50, status_bar.toggle_pulse)
	if len(args) == 0:
		function()
	else:
		function(args)
	GLib.timeout_add(50, status_bar.toggle_pulse)

def get_all_packages(force=False):
	if force or not os.path.exists('repository/all_packages.json'):
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

def get_packages_by_category(category, force=False):
	if force or not os.path.exists('repository/' + category + '_packages.json'):
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

def refresh_apps(categories):
	for category in categories.keys():
		if category == 'all':
			get_all_packages(True)
		else:
			get_packages_by_category(category, True)

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
