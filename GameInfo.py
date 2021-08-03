import gi
gi.require_version("Gtk", "3.0")
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Gtk
import os


class GameInfo:
    name = ""
    icon = ""

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def get_row(self):
        try:
            pb = Pixbuf.new_from_file_at_size(self.icon, 32, 32)
        except:
            pb = None

        return [pb, self.name]