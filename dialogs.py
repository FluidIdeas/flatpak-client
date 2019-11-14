import os
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, Gio, GLib

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
        self.set_modal(True)
        self.display_text = display_text
        self.init_components()
        self.layout_components()

    def init_components(self):
        self.box = self.get_content_area()
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_text(self.display_text)
        self.progressbar.set_show_text(True)

    def layout_components(self):
        self.set_default_size(400, 70)
        self.box.pack_start(self.progressbar, True, True, 5)
        self.box.set_border_width(10)

    def set_fraction(self, value):
        self.progressbar.set_fraction(value)
        return True

    def pulse(self):
        self.progressbar.pulse()
        return True

    def done(self, text):
        self.progressbar.set_text(text)
        self.destroy()

class TerminalDialog(Gtk.Dialog):
    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self, title, parent)
        self.parent = parent
        self.set_modal(True)
        self.init_components()
        self.layout_components()
        self.show_all()

    def init_components(self):
        self.box = self.get_content_area()
        self.terminal = Vte.Terminal()
        self.close_button = Gtk.Button('Close')
        self.close_button.set_hexpand(False)
        self.close_button.set_halign(Gtk.Align.END)
        self.close_button.connect('clicked', self.on_click)
        self.box.set_border_width(5)

    def layout_components(self):
        (w, h) = self.parent.get_size()
        self.set_default_size(w * 0.75, h * 0.75)
        self.box.pack_start(self.terminal, True, True, 5)
        self.box.pack_start(self.close_button, False, False, 5)

    def start_process(self, process):
        pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT)
        self.terminal.set_pty(pty)
        response = pty.spawn_async(
            None,
            process,
            ['PATH=' + os.environ['PATH'], None],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            self.on_process_end)
        self.in_progress = True

    def on_process_end(self, pty, task):
        pass

    def on_click(self, event):
        self.destroy()
