#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject

import json
import os.path

import packagelist
import categories
import misc
import description
import dialogs
import statusbar
import threading
import multiprocessing

class GtkAlps(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='Aryalinux Package Manager')
		self.context = dict()
		self.context['mainFrame'] = self
		with open('categories.json') as fp:
			self.categories = json.load(fp)
		self.context['categories'] = self.categories
		misc.download_apps('all', self.context)
		self.packages = self.context['downloads']
		self.context['packages'] = self.packages
		self.init_menu()

		self.init_components()
		self.layout_components()
		self.finalize_ui()

	def init_components(self):
		self.main_layout = Gtk.VBox()
		self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
		self.right_paned = Gtk.Paned.new(Gtk.Orientation.VERTICAL)

		self.menubar = misc.create_main_menu(self.context)
		self.status_bar = statusbar.StatusBar(self.context, len(self.packages))
		self.category_list = categories.Categories(self.context, self.categories, self.on_category_change_new)
		self.package_list = packagelist.PackageList(self.context)
		self.description = description.Description(self.context)

		self.description_scrolled_window = Gtk.ScrolledWindow()
		self.packagelist_scrolled_window = Gtk.ScrolledWindow()

	def layout_components(self):
		self.add(self.main_layout)
		self.main_layout.pack_start(self.menubar, False, False, 0)
		self.main_layout.pack_start(self.main_paned, True, True, 0)
		self.main_layout.pack_start(self.status_bar, False, False, 0)

		self.packagelist_scrolled_window.set_hexpand(True)
		self.packagelist_scrolled_window.set_vexpand(True)
		self.description_scrolled_window.add(self.description)
		self.packagelist_scrolled_window.add(self.package_list)

		self.main_paned.add1(self.category_list)
		self.main_paned.add2(self.right_paned)
		self.right_paned.add1(self.packagelist_scrolled_window)
		self.right_paned.add2(self.description_scrolled_window)

	def finalize_ui(self):
		(width, height) = misc.get_screen_size()
		self.set_size_request(width*0.75, height*0.75)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.main_paned.set_position(width*0.75*0.25)
		self.right_paned.set_position(height*0.75*0.55)
		self.connect('destroy', Gtk.main_quit)
		self.show_all()

	def init_menu(self):
		self.context['menuActions'] = {}
		self.context['menuActions']['refresh_apps'] = self.refresh_apps
		self.context['menuActions']['update_all_apps'] = self.update_all_apps
		self.context['menuActions']['exit'] = self.exit
		self.context['menuActions']['search'] = self.search
		self.context['menuActions']['install_selected'] = self.install_selected
		self.context['menuActions']['uninstall_selected'] = self.uninstall_selected
		self.context['menuActions']['update_selected'] = self.update_selected
		self.context['menuActions']['options'] = self.options
		self.context['menuActions']['about'] = self.about

	def on_category_change_new(self, source, event):
		selection = self.category_list.get_selection()
		category = self.categories[selection.data]
		self.context['process_completed'] = False
		self.context['process_type'] = 'unbound'
		self.modal_dialog = dialogs.ProgressDialog(self, 'Downloading...')
		self.modal_dialog.show_all()
		thread = threading.Thread(target=misc.download_apps, args=[category, self.context])
		thread.start()
		GLib.timeout_add(100, self.check_and_do)

	def refresh_apps(self, source):
		self.context['process_completed'] = False
		self.context['process_type'] = 'bound'
		self.context['fraction'] = 0.0
		self.modal_dialog = dialogs.ProgressDialog(self, 'Downloading...')
		self.modal_dialog.show_all()
		thread = threading.Thread(target=misc.refresh_packages, args=[self.context, self.categories])
		thread.start()
		GLib.timeout_add(100, self.check_and_do)

	def update_progress(self):
		self.status_bar.pulse()

	def update_all_apps(self, event):
		self.modal_dialog = dialogs.TerminalDialog(self, 'Action in progress')
		self.modal_dialog.start_process(['/usr/bin/sudo', '/usr/bin/flatpak', '-y', 'update'])

	def exit(self, event):
		exit()

	def search(self, event):
		pass
	
	def install_selected(self, event):
		pass

	def update_selected(self, event):
		pass

	def uninstall_selected(self, event):
		pass

	def options(self, event):
		pass

	def about(self, event):
		pass

	def check_and_do(self):
		if self.context['process_completed'] == True:
			self.fetched_packages = self.context['downloads']
			self.package_list.clear()
			self.package_list.refresh_package_list(self.fetched_packages)
			self.modal_dialog.done('Done')
			return False
		else:
			if self.context['process_type'] == 'unbound':
				self.modal_dialog.pulse()
			else:
				self.modal_dialog.set_fraction(self.context['fraction'])
			return True

if __name__ == "__main__":
	app = GtkAlps()
	Gtk.main()
