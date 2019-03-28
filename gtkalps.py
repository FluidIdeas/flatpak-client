#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import packagelist
import categories

class GtkAlps(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Aryalinux Package Manager')
		context = dict()

		self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
		self.paned.set_position(250)
		self.add(self.paned)

		self.package_list = packagelist.PackageList(context)
		self.category_list = categories.Categories(context)
		self.paned.add1(self.category_list)
		self.paned.add2(self.package_list)

app = GtkAlps()
app.connect('destroy', Gtk.main_quit)
app.show_all()
Gtk.main()
