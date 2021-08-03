import os
from Config import Config
import gi
from Crawler import Crawler
gi.require_version('GdkPixbuf', '2.0')
gi.require_version("Gtk", "3.0")
from gi.repository.GdkPixbuf import Pixbuf

from gi.repository import Gtk


title = "GameDotExe"
config_dir = 'GameDotExe'


class GameDotExe:
    config = None

    def run_game(self, widget, cmd):
        os.system(cmd)

    def initialize(self):
        self.config = Config()

    def __init__(self):
        self.initialize()
        self.main()

    def main(self):
        games_path = self.config.get_path()
        win = Gtk.Window()
        win.set_title(title)
        win.connect("destroy", Gtk.main_quit)
        win.set_resizable(False)
        games_list = Crawler(games_path).get_list()
        box = Gtk.VBox()
        label = Gtk.Label(label="Games")
        box.pack_start(label, True, True, 0)
        for game in games_list:
            print(game.icon)
            button = Gtk.Button(label=game.name)
            try:
                pb = Pixbuf.new_from_file_at_size(game.icon, 32, 32)
            except:
                pb = None
            if not pb == None:
                image = Gtk.Image()
                image.set_from_pixbuf(pb)
                button.set_image(image)
                button.set_always_show_image(True)

            button.connect("clicked", self.run_game, game.exec)
            box.pack_start(button, True, True, 0)
        win.add(box)
        win.show_all()
        Gtk.main()


main = GameDotExe()
