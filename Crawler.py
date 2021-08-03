import configparser
import os
from copy import copy

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from GameInfo import GameInfo

class Crawler:
    games_list = Gtk.ListStore(Pixbuf, str)
    games_list_original = Gtk.ListStore(Pixbuf, str)
    game_exec = []

    def __init__(self, path):
        print("Found game path:" + path)
        print("Search directories in " + path)
        print(os.listdir(path))
        for game in os.listdir(path):
            game_path = path + '/' + game + '/';
            ini_file = game_path + game + '.ini'
            cfg_file = game_path + 'dosbox.cfg'
            config = configparser.ConfigParser()
            config.read(ini_file)
            exec_path = config['Gameinfo']['exec']
            if not os.path.isfile(cfg_file):
                config = configparser.ConfigParser()
                with open(cfg_file, 'a') as f:
                    f.write("[sdl]\n")
                    f.write("fullscreen = true\n")
                    f.write("fullresolution = desktop\n")
                    f.write("output = opengl\n\n")
                    f.write("[autoexec]\n")
                    f.write('MOUNT C ' + game_path + "data/\n")
                    f.write('C:\n')
                    f.write(exec_path)
                    f.close()

            if (os.path.isfile(ini_file) and os.path.isfile(cfg_file)):
                config = configparser.ConfigParser()
                config.read(ini_file)
                game_name = config['Gameinfo']['name']
                print("Found game:" + game_name)
                icon_file = game_path + config['Gameinfo']['icon']
                exec_cmd = "dosbox -conf " + cfg_file
                game_info = GameInfo(game_name, icon_file)
                self.game_exec.append([game_name, exec_cmd])

                self.games_list.append(game_info.get_row())
                self.games_list_original.append(game_info.get_row())

    def get_list(self):
        return self.games_list

    def get_original_list(self):
        return self.games_list_original

    def get_exec(self, name):
        for item in self.game_exec:
            if item[0] == name:
                print(item[0])
                return item[1]



