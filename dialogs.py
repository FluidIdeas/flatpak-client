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

class ProgressDialog(Gtk.Dialog):
    def __init__(self, parent, display_text):
        Gtk.Dialog.__init__(self, "Work in progress", parent)
        self.display_text = display_text
        self.init_components()
        self.layout_components()

    def init_components(self):
        self.box = self.get_content_area()
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_text(self.display_text)
        self.progressbar.set_show_text(True)
        #self.button = Gtk.Button('Cancel')
        #self.button.connect('clicked', self.on_click)

    def layout_components(self):
        self.set_default_size(300, 90)
        self.box.pack_start(self.progressbar, True, True, 5)
        #self.box.pack_start(self.button, False, False, 5)
        self.box.set_border_width(10)

    def pulse(self, value):
        self.progressbar.set_fraction(value)
        return True

    def done(self, text):
        self.progressbar.set_text(text)

    #def on_click(self, event):
    #    self.done('Cancelling...')
    #    self.destroy()