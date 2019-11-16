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
import subprocess

import dialogs

def get_screen_size():
	display = Gdk.Display.get_default()
	monitor = display.get_primary_monitor()
	geometry = monitor.get_geometry()
	width = geometry.width
	height = geometry.height
	return (width, height)

def get_file_for_category(category):
	return category.lower() + '_packages.json'

def download_apps(category, context, force=False):
	if force or not os.path.exists('repository/' + get_file_for_category(category)):
		if category == 'all':
			url = 'https://flathub.org/api/v1/apps'
		else:
			url = 'https://flathub.org/api/v1/apps/category/' + category
		timestamp = time.time() * 1000
		process = subprocess.Popen('curl -s ' + url + ' > /tmp/' + str(timestamp) + '.gtkalps.pkgs', shell=True)
		process.communicate()
		with open('/tmp/' + str(timestamp) + '.gtkalps.pkgs', 'r') as fp:
			context['downloads'] = json.load(fp)
			with open('repository/' + get_file_for_category(category), 'w') as fp1:
				json.dump(packages, fp1)
			context['process_completed'] = True
		if os.path.exists('/tmp/' + str(timestamp) + '.gtkalps.pkgs'):
			os.remove('/tmp/' + str(timestamp) + '.gtkalps.pkgs')
	else:
		with open('repository/' + get_file_for_category(category), 'r') as fp:
			context['downloads'] = json.load(fp)
			context['process_completed'] = True
	for package in context['downloads']:
		package['status'] = package['flatpakAppId'] in context['active_apps']

def refresh_packages(context, categories):
	i = 0
	for key, category in categories.items():
		if category == 'all':
			url = 'https://flathub.org/api/v1/apps'
		elif category != '':
			url = 'https://flathub.org/api/v1/apps/category/' + category
		elif category == '':
			i = i + 1
			context['fraction'] = 1.0
			time.sleep(1)
			continue
		timestamp = time.time() * 1000
		process = subprocess.Popen('curl -s "' + url + '" > /tmp/' + str(timestamp) + '.gtkalps.pkgs', shell=True)
		process.communicate()
		with open('/tmp/' + str(timestamp) + '.gtkalps.pkgs', 'r') as fp:
			data = fp.read().strip()
			packages = json.loads(data)
			for package in packages:
				package['status'] = package['flatpakAppId'] in context['active_apps']
			with open('repository/' + get_file_for_category(category), 'w') as fp1:
				json.dump(packages, fp1)
		i = i + 1
		context['fraction'] = i/len(categories)
		if os.path.exists('/tmp/' + str(timestamp) + '.gtkalps.pkgs'):
			os.remove('/tmp/' + str(timestamp) + '.gtkalps.pkgs')
	context['process_completed'] = True

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
	menubar.append(create_menu('_Flatpak', ['_Refresh Apps', '', '_Exit'], [
		context['menuActions']['refresh_apps'],
		None,
		context['menuActions']['exit']]))
	menubar.append(create_menu('_Apps', ['_Search', '', '_Apply Selections', '_Update All Apps'], [
		context['menuActions']['search'],
		None,
		context['menuActions']['apply_selections'],
		context['menuActions']['update_all_apps']]))
	menubar.append(create_menu('_Settings', ['_Options'], [
		context['menuActions']['options']]))
	menubar.append(create_menu('_Help', ['_About'], [
		context['menuActions']['about']]))
	return menubar

def get_installed_apps(context):
	process = subprocess.Popen('flatpak list --columns=application,version', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = process.communicate()
	lines = out.decode('utf8').split('\n')
	installed = dict()
	for line in lines:
		if '\t' in line:
			parts = line.strip().split('\t')
			if len(parts) > 1:
				installed[parts[0]] = parts[1]
			else:
				installed[parts[0]] = ''
	context['installed_apps'] = installed
	installed_app_ids = []
	for key in installed.keys():
		installed_app_ids.append(key)
	return installed_app_ids

def get_installed_version(context, flatpakAppId):
	return context['installed_apps'][flatpakAppId] if flatpakAppId in context['installed_apps'] else None

def search_apps(context, keywords):
	process = subprocess.Popen('flatpak search ' + keywords, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = process.communicate()
	lines = out.decode('utf8').split('\n')
	results = []
	for line in lines:
		if '\t' in line:
			results.append(line.strip().split('\t')[2])
	context['downloads'] = []
	for item in results:
		for package in context['packages']:
			if package['flatpakAppId'] == item:
				context['downloads'].append(package)
				package['status'] = package['flatpakAppId'] in context['active_apps']
				break
	context['process_completed'] = True

def is_installed(context, appId):
	installed = get_installed_apps(context)
	return appId in installed

def install_app(widget, *data):
	context = data[0]
	dialog = Gtk.MessageDialog(parent=context['mainFrame'], flags=0, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text="Install app")
	dialog.format_secondary_text("Are you sure you want to install " + context['current_app']['name'] + '?')
	response = dialog.run()
	if response == Gtk.ResponseType.YES:
		dialog.destroy()
		with open('/tmp/.flatpak-run.sh', 'w') as fp:
			fp.write('#!/bin/bash\n\n')
			fp.write('set -e\n')
			fp.write('set +h\n\n')
			fp.write('/usr/bin/sudo /usr/bin/flatpak -y install ' + context['current_app']['flatpakAppId'] + '\n')
			fp.write('sudo update-desktop-database' + '\n\n')
		data[0]['action'] = 'apply-changes'
		modal_dialog = dialogs.TerminalDialog(context['mainFrame'], 'Action in progress', context)
		modal_dialog.start_process(['/bin/bash', '/tmp/.flatpak-run.sh'])

def remove_app(widget, *data):
	context = data[0]
	dialog = Gtk.MessageDialog(parent=context['mainFrame'], flags=0, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text="Uninstall app")
	dialog.format_secondary_text("Are you sure you want to uninstall " + context['current_app']['name'] + '?')
	response = dialog.run()
	if response == Gtk.ResponseType.YES:
		dialog.destroy()
		with open('/tmp/.flatpak-run.sh', 'w') as fp:
			fp.write('#!/bin/bash\n\n')
			fp.write('set -e\n')
			fp.write('set +h\n\n')
			fp.write('/usr/bin/sudo /usr/bin/flatpak -y uninstall ' + context['current_app']['flatpakAppId'] + '\n')
			fp.write('sudo update-desktop-database' + '\n\n')
		data[0]['action'] = 'apply-changes'
		modal_dialog = dialogs.TerminalDialog(context['mainFrame'], 'Action in progress', context)
		modal_dialog.start_process(['/bin/bash', '/tmp/.flatpak-run.sh'])

def update_app(widget, *data):
	context = data[0]
	dialog = Gtk.MessageDialog(parent=context['mainFrame'], flags=0, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text="Update app")
	dialog.format_secondary_text("Are you sure you want to update " + context['current_app']['name'] + '?')
	response = dialog.run()
	if response == Gtk.ResponseType.YES:
		dialog.destroy()
		with open('/tmp/.flatpak-run.sh', 'w') as fp:
			fp.write('#!/bin/bash\n\n')
			fp.write('set -e\n')
			fp.write('set +h\n\n')
			fp.write('/usr/bin/sudo /usr/bin/flatpak -y update ' + context['current_app']['flatpakAppId'] + '\n')
			fp.write('sudo update-desktop-database' + '\n\n')
		data[0]['action'] = 'apply-changes'
		modal_dialog = dialogs.TerminalDialog(context['mainFrame'], 'Action in progress', context)
		modal_dialog.start_process(['/bin/bash', '/tmp/.flatpak-run.sh'])