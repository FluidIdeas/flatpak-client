import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WaitDialog(Gtk.Dialog):
    def __init__(self, parent, display_text):
        Gtk.Dialog.__init__(self, "Processing...", parent)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(150, 100)
        label = Gtk.Label(display_text)
        box = self.get_content_area()
        box.add(label)
        box.set_border_width(10)
        self.show_all()