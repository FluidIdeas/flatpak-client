import gi
from gi.repository import Gtk
import misc

# This list is supposed to show the list of all available flatpaks
# The following information is shown in tabular format:
# Install?, name, summary, current version, latest release date
class FlatpakList(Gtk.TreeView):
	def __init__(self, context):
		Gtk.TreeView.__init__(self)
		self.context = context

		self.package_store = Gtk.ListStore(bool, str, str, str, str, str)

		self.set_model(self.package_store)

		for i, title in enumerate(['Installed', 'Name', 'Current Version', 'Release Date', 'Description', 'Flatpak ID']):
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
		self.connect('row-activated', self.onRowSelection)
		self.set_activate_on_single_click(True)

	def get_model(self):
		return self.package_store

	def add_package(self, package):
		row_data = [
				False,
				package['name'],
				package['currentReleaseVersion'] if 'currentReleaseVersion' in package else '',
				package['currentReleaseDate'] if 'currentReleaseDate' in package else '',
				package['summary'] if 'summary' in package else '',
				package['flatpakAppId']
		]
		self.package_store.append(row_data)

	def clear(self):
		self.package_store.clear()

	def onRowSelection(self, source, index, column):
		for i, row in enumerate(self.package_store):
			if i == int(str(index)):
				package_details = misc.get_package_details(self.package_store[index][5])
				self.context['description'].set_data(package_details)
				break

	def on_toggle(self, cell, path, model):
		if path is not None:
			it = model.get_iter(path)
			model[it][0] = not model[it][0]