import os
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, Gio, GLib
import misc

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
    def __init__(self, parent, title, context):
        Gtk.Dialog.__init__(self, title, parent)
        self.parent = parent
        self.context = context
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

class EntryDialog(Gtk.Dialog):
    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self, title, parent)
        self.parent = parent
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.set_modal(True)
        self.init_components()
        self.layout_components()
        self.show_all()

    def init_components(self):
        self.box = self.get_content_area()
        self.text_box = Gtk.Entry()
        self.box.set_border_width(5)

    def layout_components(self):
        self.box.pack_start(self.text_box, True, False, 5)
        (w, h) = self.parent.get_size()
        self.set_default_size(450, -1)

    def get_data(self):
        return self.text_box.get_text()

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self, title, parent)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.set_modal(True)
        self.parent = parent
        self.init_components()
        self.layout_components()
        self.show_all()

    def init_components(self):
        self.box = self.get_content_area()
        self.main_notebook = Gtk.Notebook()
        self.proxy_tab = ProxyTab()
        self.proxy_tab.set_hexpand(True)

    def layout_components(self):
        self.main_notebook.append_page(self.proxy_tab, Gtk.Label('Proxy Settings'))
        self.main_notebook.set_hexpand(True)
        self.main_notebook.set_vexpand(True)
        self.box.set_border_width(5)
        self.box.set_spacing(5)
        self.box.add(self.main_notebook)
        (w, h) = self.parent.get_size()
        self.set_default_size(600, 350)

class ProxyTab(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(5)
        self.set_row_spacing(5)
        self.init_components()
        self.layout_components()
        self.set_border_width(5)

    def init_components(self):
        self.use_proxy_switch = Gtk.Switch()
        self.use_proxy_switch.connect('notify::active', self.on_switch_activated)
        self.use_proxy_switch.set_halign(Gtk.Align.START)

        self.server = Gtk.Entry()
        self.server.set_hexpand(True)
        self.port = Gtk.Entry()
        self.port.set_hexpand(True)
        self.username = Gtk.Entry()
        self.username.set_hexpand(True)
        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_hexpand(True)

        self.enable_label = self.create_label('Enable Proxy')
        self.server_label = self.create_label('Server')
        self.port_label = self.create_label('Port')
        self.username_label = self.create_label('Username')
        self.password_label = self.create_label('Password')

    def create_label(self, text):
        label = Gtk.Label(text)
        label.set_halign(Gtk.Align.END)
        label.set_hexpand(False)
        return label

    def on_switch_activated(self, switch, gparam):
        if switch.get_active():
            self.use_proxy = True
        else:
            self.use_proxy = False

    def add_component(self, component, x, y, w, h):
        self.attach(component, x, y, w, h)

    def layout_components(self):
        self.add_component(self.enable_label, 0, 0, 1, 1)
        self.add_component(self.server_label, 0, 1, 1, 1)
        self.add_component(self.port_label, 0, 2, 1, 1)
        self.add_component(self.username_label, 0, 3, 1, 1)
        self.add_component(self.password_label, 0, 4, 1, 1)

        self.add_component(self.use_proxy_switch, 1, 0, 1, 1)
        self.add_component(self.server, 1, 1, 1, 1)
        self.add_component(self.port, 1, 2, 1, 1)
        self.add_component(self.username, 1, 3, 1, 1)
        self.add_component(self.password, 1, 4, 1, 1)

    def get_data(self):
        return {
            'enableProxy': self.use_proxy_switch.get_state(),
            'server': self.server.get_text(),
            'port': self.port.get_text(),
            'username': self.username.get_text(),
            'password': self.password.get_text()
        }

    def set_data(self, data):
        self.use_proxy_switch.set_state(data['enableProxy'])
        self.server.set_text(data['server'])
        self.port.set_text(data['port'])
        self.username.set_text(data['username'])
        self.password.set_text(data['password'])