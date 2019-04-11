import gi
from gi.repository import Gtk

class Categories(Gtk.VBox):
	def __init__(self, context):
		Gtk.VBox.__init__(self)
		self.context = context

		self.categories_list = ['All', 'Miscellaneous', 'Internet and Network', 'Desktop Environment', 'Image, Audio and Video']

		self.categories = Gtk.ListBox()
		self.categories.set_selection_mode(Gtk.SelectionMode.SINGLE)

		for category in self.categories_list:
			list_box_row = Gtk.ListBoxRow()
			list_box_row.data = category
			list_box_row.add(Gtk.Label(category, xalign=0))
			self.categories.add(list_box_row)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.add(self.categories)
		scrolled_window.set_hexpand(True)
		scrolled_window.set_vexpand(True)

		self.pack_start(scrolled_window, False, True, 0)

