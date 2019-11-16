import gi
from gi.repository import Gtk

class Categories(Gtk.VBox):
	def __init__(self, context, category_dict, on_selection):
		Gtk.VBox.__init__(self)
		self.context = context

		self.categories_list = category_dict.keys()

		self.categories = Gtk.ListBox()
		self.categories.set_selection_mode(Gtk.SelectionMode.SINGLE)

		self.rows = list()

		for category in self.categories_list:
			list_box_row = Gtk.ListBoxRow()
			list_box_row.data = category
			list_box_row.add(Gtk.Label(category, xalign=0))
			self.categories.add(list_box_row)
			self.rows.append(list_box_row)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.add(self.categories)
		scrolled_window.set_hexpand(True)
		scrolled_window.set_vexpand(True)

		self.pack_start(scrolled_window, False, True, 0)
		self.categories.select_row(self.rows[0])
		self.on_selection = on_selection
		self.categories.connect('row-selected', on_selection)

	def select(self, row):
		self.categories.select(row)

	def get_selection(self):
		return self.categories.get_selected_row()

	def select_row(self, index):
		if self.get_selection().get_index() == index:
			self.on_selection(None, None)
		self.categories.select_row(self.rows[index])
