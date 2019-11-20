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
    def __init__(self, parent, context):
        Gtk.Dialog.__init__(self, parent)
        self.set_title('Working...')
        self.set_modal(True)
        #self.display_text = display_text
        self.init_components()
        self.layout_components()

    def init_components(self):
        self.box = self.get_content_area()
        self.progressbar = Gtk.ProgressBar()
        #self.progressbar.set_text(self.display_text)
        #self.progressbar.set_show_text(True)

    def layout_components(self):
        self.set_default_size(400, -1)
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

    def get_data(self):
        return {
            'proxy': self.proxy_tab.get_data()
        }

    def set_data(self, data):
        if 'proxy' in data:
            self.proxy_tab.set_data(data['proxy'])

class ProxyTab(Gtk.VBox):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.init_components()
        self.layout_components()
        self.set_border_width(10)

    def init_components(self):
        self.use_proxy_switch = Gtk.Switch()
        self.use_proxy_switch.set_state(False)
        self.use_proxy_switch.connect('notify::active', self.on_switch_activated)
        self.use_proxy_switch.set_halign(Gtk.Align.END)
        self.same_settings = Gtk.CheckButton.new_with_label('Use this proxy server for all protocols')
        self.same_settings.connect('toggled', self.on_toggle_same_settings)

        self.enable_label = self.create_label('Enable Proxy')
        self.server_label = self.create_label('Server')
        self.port_label = self.create_label('Port')
        self.username_label = self.create_label('Username')
        self.password_label = self.create_label('Password')

        self.grid, self.controls = self.create_widget_group()

    def create_widget_group(self):
        controls = []
        for i in range(4):
            server = Gtk.Entry()
            port = Gtk.Entry()
            username = Gtk.Entry()
            password = Gtk.Entry()
            server.set_hexpand(True)
            port.set_hexpand(True)
            password.set_hexpand(True)
            password.set_sensitive(True)
            controls.append({
                'server': server,
                'port': port,
                'username': username,
                'password': password
            })
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(3)
        grid.set_row_spacing(3)

        self.header = Gtk.HBox()
        self.enable_label.set_halign(Gtk.Align.START)
        self.header.pack_start(self.use_proxy_switch, False, False, 5)
        self.header.pack_start(self.enable_label,True, True, 5)
        
        grid.attach(self.server_label, 0, 1, 1, 1)
        grid.attach(self.port_label, 1, 1, 1, 1)
        grid.attach(self.username_label, 2, 1, 1, 1)
        grid.attach(self.password_label, 3, 1, 1, 1)

        # Attaching the first set of entries
        grid.attach(controls[0]['server'], 0, 2, 1, 1)
        grid.attach(controls[0]['port'], 1, 2, 1, 1)
        grid.attach(controls[0]['username'], 2, 2, 1, 1)
        grid.attach(controls[0]['password'], 3, 2, 1, 1)

        grid.attach(self.same_settings, 1, 3, 3, 1)
        for i in range(3, 6):
            grid.attach(controls[i - 2]['server'], 0, i + 1, 1, 1)
            grid.attach(controls[i - 2]['port'], 1, i + 1, 1, 1)
            grid.attach(controls[i - 2]['username'], 2, i + 1, 1, 1)
            grid.attach(controls[i - 2]['password'], 3, i + 1, 1, 1)
        return grid, controls

    def create_label(self, text):
        label = Gtk.Label(text)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(False)
        return label

    def on_switch_activated(self, switch, gparam):
        if switch.get_active():
            self.use_proxy = True
            self.grid.set_sensitive(True)
        else:
            self.use_proxy = False
            self.grid.set_sensitive(False)

    def add_component(self, component, x, y, w, h):
        self.attach(component, x, y, w, h)

    def layout_components(self):
        self.pack_start(self.header, False, True, 5)
        self.pack_start(self.grid, True, True, 5)

    def get_data(self):
        result = {
            'enableProxy': self.use_proxy_switch.get_state(),
            'useSameSettings': self.same_settings.get_active(),
            'proxy': []
        }
        for i in range(len(self.controls)):
            result['proxy'].append({
                'server': self.controls[i]['server'].get_text(),
                'port': self.controls[i]['port'].get_text(),
                'username': self.controls[i]['username'].get_text(),
                'password': self.controls[i]['password'].get_text()
            })
        return result

    def set_data(self, data):
        self.use_proxy_switch.set_state(data['enableProxy'])
        self.controls[0]['server'].set_text(data['proxy'][0]['server'])
        self.controls[0]['port'].set_text(data['proxy'][0]['port'])
        self.controls[0]['username'].set_text(data['proxy'][0]['username'])
        self.controls[0]['password'].set_text(data['proxy'][0]['password'])
        if data['useSameSettings']:
            for i in range(1, 4):
                self.controls[i]['server'].set_text(data['proxy'][0]['server'])
                self.controls[i]['port'].set_text(data['proxy'][0]['port'])
                self.controls[i]['username'].set_text(data['proxy'][0]['username'])
                self.controls[i]['password'].set_text(data['proxy'][0]['password'])
        else:
            for i in range(1, 4):
                self.controls[i]['server'].set_text(data['proxy'][i]['server'])
                self.controls[i]['port'].set_text(data['proxy'][i]['port'])
                self.controls[i]['username'].set_text(data['proxy'][i]['username'])
                self.controls[i]['password'].set_text(data['proxy'][i]['password'])
        self.same_settings.set_active(data['useSameSettings'])
        if not data['enableProxy']:
            self.grid.set_sensitive(False)
        else:
            self.grid.set_sensitive(True)

    def on_toggle_same_settings(self, widget):
        if not widget.get_active():
            for i in range(1, 4):
                self.controls[i]['server'].set_sensitive(True)
                self.controls[i]['port'].set_sensitive(True)
                self.controls[i]['username'].set_sensitive(True)
                self.controls[i]['password'].set_sensitive(True)
        else:
            for i in range(1, 4):
                self.controls[i]['server'].set_text(self.controls[0]['server'].get_text())
                self.controls[i]['port'].set_text(self.controls[0]['port'].get_text())
                self.controls[i]['username'].set_text(self.controls[0]['username'].get_text())
                self.controls[i]['password'].set_text(self.controls[0]['password'].get_text())
                self.controls[i]['server'].set_text(self.controls[0]['server'].get_text())

                self.controls[i]['server'].set_sensitive(False)
                self.controls[i]['port'].set_sensitive(False)
                self.controls[i]['username'].set_sensitive(False)
                self.controls[i]['password'].set_sensitive(False)