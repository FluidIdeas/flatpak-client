import gi
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import WebKit2
import urllib.request
import misc

class Description(Gtk.VBox):
    def __init__(self, context):
        Gtk.VBox.__init__(self)
        self.context = context
        self.context['description'] = self
        self.current_app = None
        self.create_components()
        self.add_components()

        self.set_border_width(10)

    def create_components(self):
        self.left_box = Gtk.VBox()
        self.left_box.set_hexpand(True)
        self.button_box = Gtk.HBox()
        self.right_box = Gtk.VBox()
        self.line1 = Gtk.HBox()
        self.line1.set_homogeneous(True)
        self.line2 = Gtk.HBox()
        self.line2.set_homogeneous(True)

        self.heading = Gtk.Label()
        self.heading.set_markup('<span size="xx-large"></span>')
        self.heading.set_hexpand(True)
        self.heading.set_vexpand(False)
        self.heading.set_halign(Gtk.Align.START)
        self.heading.set_valign(Gtk.Align.START)

        self.short_description = Gtk.Label('')
        self.short_description.set_hexpand(True)
        self.short_description.set_vexpand(False)
        self.short_description.set_halign(Gtk.Align.START)
        self.short_description.set_valign(Gtk.Align.START)

        self.version = Gtk.Label('Version: ')
        self.version.set_hexpand(True)
        self.version.set_vexpand(False)
        self.version.set_halign(Gtk.Align.START)
        self.version.set_valign(Gtk.Align.START)
        
        self.last_updated_date = Gtk.Label('Last Updated: ')
        self.last_updated_date.set_hexpand(True)
        self.last_updated_date.set_vexpand(False)
        self.last_updated_date.set_halign(Gtk.Align.START)
        self.last_updated_date.set_valign(Gtk.Align.START)

        self.developer = Gtk.Label('Developer: ')
        self.developer.set_hexpand(True)
        self.developer.set_vexpand(False)
        self.developer.set_halign(Gtk.Align.START)
        self.developer.set_valign(Gtk.Align.START)

        self.license = Gtk.Label('License: ')
        self.license.set_hexpand(True)
        self.license.set_vexpand(False)
        self.license.set_halign(Gtk.Align.START)
        self.license.set_valign(Gtk.Align.START)

        self.install = Gtk.Button('Install')
        self.install.set_hexpand(False)
        
        self.uninstall = Gtk.Button('Uninstall')
        self.uninstall.set_hexpand(False)
        
        self.update = Gtk.Button('Update')
        self.update.set_hexpand(False)

        self.image = Gtk.Image.new_from_file('')
        self.image.set_hexpand(True)
        self.image.set_halign(Gtk.Align.START)
        self.image.set_valign(Gtk.Align.START)

        self.details = WebKit2.WebView()
        self.details.load_html('')
        self.details.set_vexpand(True)
        settings = WebKit2.Settings()
        settings.set_default_font_family('Open Sans')
        settings.set_default_font_size(14)
        self.details.set_settings(settings)
        
        self.package_info_label = Gtk.Label()
        self.package_info_label.set_markup('<span size="xx-large">Screenshot</span>')
        self.package_info_label.set_hexpand(True)
        self.package_info_label.set_vexpand(False)
        self.package_info_label.set_halign(Gtk.Align.END)
        self.package_info_label.set_valign(Gtk.Align.START)

        self.install.connect('clicked', misc.install_app, self.context)
        self.uninstall.connect('clicked', misc.remove_app, self.context)
        self.update.connect('clicked', misc.update_app, self.context)

    def add_components(self):

        self.button_box.pack_start(self.install, False, True, 5)
        self.button_box.pack_start(self.uninstall, False, True, 5)
        self.button_box.pack_start(self.update, False, True, 5)

        self.line1.pack_start(self.version, True, True, 0)
        self.line1.pack_start(self.last_updated_date, True, True, 0)
        self.line2.pack_start(self.developer, True, True, 0)

        self.pack_start(self.heading, False, True, 5)
        self.pack_start(self.short_description, False, True, 5)
        self.pack_start(self.button_box, False, True, 5)

        self.pack_start(self.details, False, True, 0)

    def set_data(self, data):
        self.context['current_app'] = data
        self.heading.set_markup('<span size="xx-large">' + data['name'] + '</span>')
        self.short_description.set_markup(data['summary'])
        self.details.load_html(self.description_html(data))
        self.current_package_id = data['flatpakAppId']
        self.is_installed = misc.is_installed(self.context, self.current_package_id)
        if self.is_installed:
            self.install.set_sensitive(False)
            self.uninstall.set_sensitive(True)
        else:
            self.install.set_sensitive(True)
            self.uninstall.set_sensitive(False)
        if not data['currentReleaseVersion'] == misc.get_installed_version(self.context, self.current_package_id):
            self.update.set_sensitive(True)
        else:
            self.update.set_sensitive(False)

    def clear(self):
        self.heading.set_markup('<span size="xx-large"></span>')
        self.short_description.set_markup('')
        self.details.load_html('')
        self.current_package_id = ''

    def get_current_id(self):
        return self.current_package_id

    def description_html(self, data):
        image_url = 'http://aryalinux.info/images/app.png'
        if len(data['screenshots']) > 0:
            image_url = data['screenshots'][0]['imgDesktopUrl']
        release_date = '-'
        if data['currentReleaseDate'] != None:
            release_date = data['currentReleaseDate'][:data['currentReleaseDate'].index('T')]
        result = ''
        result = result + '''
        <table style="width: 100%">
            <tr>
                <td width="100%" valign="top">''' + data['description'] + '<br>' + 'Version: ' + data['currentReleaseVersion'] + '<br>' + 'Developer: ' + data['developerName'] + '<br>' + 'Last Updated on: ' + release_date + '''<br></td>
                <td valign="top"><img width="800" height="450" src="''' + image_url + '''"></td>
            </tr>
        </table>'''
        return result