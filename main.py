import os
from Handler import Handler
from Config import Config
import gi
from Crawler import Crawler
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

title = "GameDotExe"
config_dir = 'GameDotExe'

class GameDotExe:
    config = None
    crawler = None
    games_list = None

    def initialize(self):
        self.config = Config()

    def __init__(self):
        self.icon_list = None
        self.initialize()
        self.main()

    def main(self):
        games_path = self.config.get_path()
        builder = Gtk.Builder()
        builder.add_from_file("gui.glade")
        win = builder.get_object("mainWindow")
        btn_quit = builder.get_object("btn_quit")
        self.crawler = Crawler(games_path)
        self.games_list = self.crawler.get_list()
        builder.connect_signals(Handler(Crawler))
        icon_list = builder.get_object("game_icons")
        icon_list.set_model(self.games_list)
        icon_list.set_pixbuf_column(0)
        icon_list.set_text_column(1)

        win.show_all()
        Gtk.main()

    def handlers(self, widget):
        print(widget)


main = GameDotExe()
