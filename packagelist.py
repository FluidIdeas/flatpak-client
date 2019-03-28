import gi
from gi.repository import Gtk

class PackageList(Gtk.TreeView):
	def __init__(self, context):
		Gtk.TreeView.__init__(self)
		self.context = context

		self.package_store = Gtk.ListStore(bool, str, str, str, str)
		self.package_store.append([False, 'libreoffice', '6.0', '-', 'Libreoffice is a productivity suite of applications similar to Office'])

		self.set_model(self.package_store)

		for i, title in enumerate(['Installed', 'Name', 'Available version', 'Installed version', 'Description']):
			if i != 0:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(title, renderer, text=i)
			elif i == 0:
				renderer = Gtk.CellRendererToggle()
				renderer.set_property('activatable', True)
				renderer.connect("toggled", self.on_toggle, self.package_store)
				column = Gtk.TreeViewColumn(title, renderer, active=0)
			self.append_column(column)
		self.set_hexpand(True)
		self.set_vexpand(True)

	def get_model(self):
		return self.package_store

	def add_package(self, package):
		self.package_store.append(package)

	def clear(self):
		self.package_store.clear()

	def on_toggle(self, cell, path, model):
		if path is not None:
			it = model.get_iter(path)
			model[it][0] = not model[it][0]


