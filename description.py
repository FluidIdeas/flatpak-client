import gi
from gi.repository import Gtk

class GeneralPanel(Gtk.Table):
    def __init__(self):
        Gtk.Table.__init__(self)
        self.set_row_spacings(5)
        self.set_col_spacings(5)

    def add_component(self, component, x, y, w, h, hexpand=Gtk.AttachOptions.FILL, vexpand=Gtk.AttachOptions.FILL):
        self.attach(component, x, x+w, y, y+h, hexpand, vexpand)

    def filler(self):
        filler = Gtk.Label('')
        filler.set_hexpand(True)
        return filler

class PackageInformation(GeneralPanel):
    def __init__(self):
        GeneralPanel.__init__(self)
        self.create_components()
        self.add_components()

    def create_components(self):
        self.heading = Gtk.Label('')
        self.heading.set_markup('<span size="large">Package Information</span>')
        self.last_updated_date = Gtk.Label('Last Updated:')
        self.license = Gtk.Label('License:')
        self.version = Gtk.Label('Version:')
        self.category = Gtk.Label('Category:')

    def add_components(self):
        self.add_component(self.heading, 0, 0, 1, 1)
        self.add_component(self.version, 0, 1, 1, 1)
        self.add_component(self.category, 0, 2, 1, 1)
        self.add_component(self.category, 0, 3, 1, 1)
        self.add_component(self.last_updated_date, 0, 4, 1, 1)

class ActionsPanel(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)
        self.install = Gtk.Button('Install')
        self.uninstall = Gtk.Button('Uninstall')
        self.update = Gtk.Button('Update')

        self.pack_start(self.install, False, False, 5)
        self.pack_start(self.uninstall, False, False, 5)
        self.pack_start(self.update, False, False, 5)

class Header(GeneralPanel):
    def __init__(self):
        GeneralPanel.__init__(self)
        self.package_name = self.name_label()
        self.short_description = self.short_description_label()
        self.action_panel = self.action_panel()
        self.add_components()

    def name_label(self):
        package_name = Gtk.Label('')
        package_name.set_markup('<span size="xx-large">Package Name</span>')
        package_name.set_hexpand(False)
        package_name.set_valign(Gtk.Align.START)
        package_name.set_halign(Gtk.Align.START)
        return package_name

    def short_description_label(self):
        short_description = Gtk.Label('This is where the short description would appear.')
        short_description.set_halign(Gtk.Align.START)
        return short_description

    def action_panel(self):
        action_panel = ActionsPanel()
        action_panel.set_valign(Gtk.Align.START)
        return action_panel

    def add_components(self):
        self.add_component(self.package_name, 0, 0, 1, 1)
        self.add_component(self.filler(), 1, 0, 1, 1)
        self.add_component(self.action_panel, 2, 0, 1, 1)
        self.add_component(self.short_description, 0, 1, 1, 1)

class Description(GeneralPanel):
    def __init__(self):
        GeneralPanel.__init__(self)
        self.create_components()
        self.add_components()
        self.set_border_width(10)

    def create_components(self):
        self.header = Header()
        self.header.set_hexpand(True)
        self.info = PackageInformation()

    def add_components(self):
        self.add_component(self.header, 0, 0, 2, 1, hexpand=Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        self.add_component(self.info, 1, 1, 1, 1)
