#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import packagelist
import categories
import misc

class GtkAlps(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Aryalinux Package Manager')
		context = dict()

		self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
		self.paned.set_position(250)
		self.add(self.paned)

		self.packages = misc.load_packages()
		context['packages'] = self.packages
		self.package_list = packagelist.PackageList(context)
		self.package_list.clear()
		for package in self.packages:
			self.package_list.add_package(package)
		self.category_list = categories.Categories(context)
		self.paned.add1(self.category_list)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.add(self.package_list)
		scrolled_window.set_hexpand(True)
		scrolled_window.set_vexpand(True)
		self.paned.add2(scrolled_window)

		screen = Gdk.Screen.get_default()
		self.set_size_request(screen.get_width()*0.75, screen.get_height()*0.75)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

app = GtkAlps()
app.connect('destroy', Gtk.main_quit)
app.show_all()
Gtk.main()
