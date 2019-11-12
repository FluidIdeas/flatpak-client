import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

class StatusBar(Gtk.HBox):
    def __init__(self, context, count):
        Gtk.HBox.__init__(self)
        self.count = count
        self.context = context
        self.init_components()
        self.add_components()
        self.source_id = 0
        self.context['statusBar'] = self
        self.set_border_width(5)

    def init_components(self):
        self.status_label = Gtk.Label('Welcome to FlatHub Manager')
        self.stats_label = Gtk.Label('Total Packages: ' + str(self.count))
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_text('Progress ')
        self.progressbar.set_show_text(True)

    def add_components(self):
        self.stats_label.set_halign(Gtk.Align.START)
        self.status_label.set_halign(Gtk.Align.START)
        self.progressbar.set_halign(Gtk.Align.START)
        self.pack_start(self.status_label, True, True, 2)
        self.pack_start(self.stats_label, True, False, 2)
        self.pack_start(self.progressbar, False, False, 2)

    def toggle_pulse(self):
        if self.source_id == 0:
            self.source_id = GLib.timeout_add(50, self.pulse)
        else:
            GLib.source_remove(self.source_id)
            self.source_id = 0
            self.progressbar.set_fraction(0.0)

    def pulse(self):
        self.progressbar.pulse()
        return False

    def set_status_message(self, text):
        self.status_label.set_text(text)

    def set_stats_label(self, text):
        self.stats_label.set_text(text)
    