import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk


class Dialog:
    configfile = ''
    dialog = None

    def select_game_folder(self):
        self.dialog = Gtk.FileChooserDialog(
            title="Choose game folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        self.dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        self.dialog.set_default_size(800, 400)
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + self.dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        return self.dialog.get_filename()
