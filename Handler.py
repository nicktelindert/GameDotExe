import gi
import os
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Handler:
    crawler = None
    search_term = None

    def __init__(self, crawler):
        self.crawler = crawler

    def btn_quit_clicked(self, widget):
        Gtk.main_quit()

    def launch_application(self, widget, idx):
        iter = widget.get_model().get_iter_from_string(idx.to_string())
        os.system(self.crawler.get_exec(self.crawler, widget.get_model().get_value(iter, 1)))

    def set_search_term(self, widget):
        self.search_term = widget.get_text()

    def search_list(self, button):
        if not self.search_term == None:
            regex = re.compile(".*" + self.search_term.lower() + ".*$")

            self.crawler.games_list.clear()
            for game_icon in self.crawler.get_original_list(self.crawler):
                matches = re.match(regex, game_icon[1].lower())
                if matches:
                    self.crawler.games_list.append([game_icon[0], game_icon[1]])