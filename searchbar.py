#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SearchBar(Gtk.HBox):
    def __init__(self, context):
        Gtk.HBox.__init__(self)
        self.context = context
        self.init_components()
        self.layout_components()

    def init_components(self):
        self.search_label = Gtk.Label('Search Apps: ')
        self.search_box = Gtk.Entry()
        self.search_button = Gtk.Button('Go')
        self.search_button.connect('clicked', self.on_search)
        self.search_box.connect('activate', self.on_search)
        self.set_border_width(5)

    def layout_components(self):
        self.pack_start(self.search_label, False, False, 5)
        self.pack_start(self.search_box, True, True, 5)
        self.pack_start(self.search_button, False, False, 5)

    def on_search(self, widget):
        keywords = self.search_box.get_text()
        self.context['categories']['Search Results'] = keywords
        self.context['category_list'].select_row(len(self.context['categories']) - 1)