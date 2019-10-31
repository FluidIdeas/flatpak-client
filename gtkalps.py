#!/usr/bin/env python2

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import json

import flatpaklist
import packagelist
import categories
import misc
import description

class GtkAlps(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Aryalinux Package Manager')
		context = dict()

		with open('categories.json') as fp:
			self.categories = json.load(fp)

		self.root_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
		self.internal_paned = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
		self.add(self.root_paned)

		self.flatpaks = misc.get_all_packages()
		for p in self.flatpaks:
			p['status'] = False
			if None != p['currentReleaseDate']:
				p['currentReleaseDate'] = p['currentReleaseDate'][:p['currentReleaseDate'].index('T')]
		context['packages'] = self.flatpaks
		self.package_list = flatpaklist.FlatpakList(context)
		self.package_list.clear()
		for package in self.flatpaks:
			self.package_list.add_package(package)
		self.category_list = categories.Categories(context, self.categories, self.on_category_change)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.add(self.package_list)
		scrolled_window.set_hexpand(True)
		scrolled_window.set_vexpand(True)

		self.root_paned.add1(self.category_list)
		self.root_paned.add2(self.internal_paned)
		self.internal_paned.add1(scrolled_window)
		self.internal_paned.add2(description.Description())

		(width, height) = self.get_screen_size()
		self.set_size_request(width*0.75, height*0.75)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.root_paned.set_position(screen.get_width()*0.75*0.25)
		self.internal_paned.set_position(screen.get_height()*0.75*0.55)

	def on_category_change(self, source, event):
		selection = self.category_list.get_selection()
		category = self.categories[selection.data]
		if category == 'all':
			pkgs = misc.get_all_packages()
		else:
			pkgs = misc.get_packages_by_category(category)
		self.package_list.clear()
		for package in pkgs:
			package['status'] = False
			if None != package['currentReleaseDate']:
				package['currentReleaseDate'] = package['currentReleaseDate'][:package['currentReleaseDate'].index('T')]
			self.package_list.add_package(package)

	def get_screen_size(self):
		display = Gdk.Display.get_default()
		monitor = display.get_primary_monitor()
		geometry = monitor.get_geometry()
		width = geometry.width
		height = geometry.height
		return (width, height)

app = GtkAlps()
app.connect('destroy', Gtk.main_quit)
app.show_all()
Gtk.main()
