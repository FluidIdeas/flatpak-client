import gi
from gi.repository import Gtk

class PackageList(Gtk.TreeView):
	def __init__(self, context):
		Gtk.TreeView.__init__(self)
		self.context = context

		self.package_store = Gtk.ListStore(bool, str, str, str, str, str, bool)

		self.set_model(self.package_store)

		for i, title in enumerate(['Installed', 'Name', 'Available version', 'Installed version', 'Installed Date', 'Description']):
			if i != 0:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(title, renderer, text=i)
			elif i == 0:
				renderer = Gtk.CellRendererToggle()
				renderer.set_property('activatable', True)
				renderer.connect("toggled", self.on_toggle, self.package_store)
				column = Gtk.TreeViewColumn(title, renderer, active=0)
				column.add_attribute(renderer, 'activatable', 6)
			self.append_column(column)
		self.set_hexpand(True)
		self.set_vexpand(True)

	def get_model(self):
		return self.package_store

	def add_package(self, package):
		row_data = [
				package['status'],
				package['name'],
				package['available_version'],
				package['version'] if 'version' in package else '' ,
				package['installed_date'] if 'installed_date' in package else '',
				package['description'] if 'description' in package else '',
				not package['status']
		]
		self.package_store.append(row_data)

	def clear(self):
		self.package_store.clear()

	def on_toggle(self, cell, path, model):
		if path is not None:
			it = model.get_iter(path)
			model[it][0] = not model[it][0]


