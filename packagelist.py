import gi
from gi.repository import Gtk, GLib
import misc
import threading

# This list is supposed to show the list of all available flatpaks
# The following information is shown in tabular format:
# Install?, name, summary, current version, latest release date
class PackageList(Gtk.TreeView):
	def __init__(self, context):
		Gtk.TreeView.__init__(self)
		self.context = context
		self.package_store = Gtk.ListStore(bool, str, str, str, str, str)
		self.set_model(self.package_store)

		self.get_font_color()
		for i, title in enumerate(['Installed', 'Name', 'Current Version', 'Release Date', 'Description', 'Flatpak ID']):
			if i != 0:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(title, renderer, text=i)
			elif i == 0:
				renderer = Gtk.CellRendererToggle()
				renderer.set_property('activatable', True)
				renderer.connect("toggled", self.on_toggle, self.package_store)
				column = Gtk.TreeViewColumn(title, renderer, active=0)
			column.set_cell_data_func(renderer, self.background_color_function)
			self.append_column(column)
		self.set_hexpand(True)
		self.set_vexpand(True)
		self.connect('row-activated', self.onRowSelection)
		self.set_activate_on_single_click(True)

	def get_font_color(self):
		self.font_color = self.rgba_to_hex(self.get_style_context().get_color(Gtk.StateType.NORMAL))
		
	def rgba_to_hex(self, color):
		return "#{0:02x}{1:02x}{2:02x}".format(int(color.red  * 255), int(color.green * 255), int(color.blue * 255))

	def background_color_function(self, column, cell, model, iter, user_data):
		installed = model.get_value(iter, 0)
		if installed:
			if isinstance(cell, Gtk.CellRendererText):
				cell.set_property('cell-background','#008000')
				cell.set_property('foreground', '#ffffff')
			else:
				cell.set_sensitive(False)
		else:
			if isinstance(cell, Gtk.CellRendererText):
				cell.set_property('cell-background','#ffffff')
				cell.set_property('foreground', self.font_color)
			else:
				cell.set_sensitive(False)
		pass 

	def refresh_package_list(self):
		for package in self.context['downloads']:
			package['status'] = package['flatpakAppId'] in self.context['active_apps']
			if None != package['currentReleaseDate'] and 'T' in package['currentReleaseDate']:
				package['currentReleaseDate'] = package['currentReleaseDate'][:package['currentReleaseDate'].index('T')]
			self.add_package(package)
		self.set_cursor(0)
		self.onRowSelection(None, 0, None)

	def get_model(self):
		return self.package_store

	def add_package(self, package):
		row_data = [
				package['status'],
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
		self.selection_params = {
			'source': source,
			'index': index,
			'column': column
		}
		flatpakAppId = self.package_store[self.selection_params['index']][5]
		status = self.package_store[self.selection_params['index']][0]
		if flatpakAppId in self.context['active_apps'] and status == False:
			self.context['active_apps'].remove(flatpakAppId)
		elif status == True:
			self.context['active_apps'].append(flatpakAppId)
		thread = threading.Thread(target=self.fetch_package_details)
		thread.daemon = True
		thread.start()

	def fetch_package_details(self):
		for i, row in enumerate(self.package_store):
			if i == int(str(self.selection_params['index'])):
				self.package_details = misc.get_package_details(self.context, self.package_store[self.selection_params['index']][5])
				self.context['description'].set_data(self.package_details)
				break

	def on_toggle(self, cell, path, model):
		if path is not None:
			it = model.get_iter(path)
			model[it][0] = not model[it][0]