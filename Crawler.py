import configparser
import os
from copy import copy
from shutil import copyfile

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

from GameInfo import GameInfo

class Crawler:
    games_list = Gtk.ListStore(Pixbuf, str)
    games_list_original = Gtk.ListStore(Pixbuf, str)
    game_exec = []
    base_path = ""

    def __init__(self, path):
        self.base_path = path
        self.assets_dir = os.path.dirname(os.path.realpath(__file__)) + "/assets"

    def build_list(self):
        path = self.base_path
        print("Found game path:" + path)
        print("Search directories in " + path)
        print(os.listdir(path))
        config = configparser.ConfigParser()

        for game in os.listdir(path):
            game_path = path + '/' + game + '/';
            ini_file = game_path + game + '.ini'
            cfg_file = game_path + 'dosbox.cfg'
            config.read(ini_file)
            exec_path = config['Gameinfo']['exec']
            mount_path = game_path + "data"

            if self.create_dosbox_config(mount_path, exec_path, cfg_file):
                print("Config exists")
                if (os.path.isfile(ini_file)):
                    config.read(ini_file)
                    if 'Gameinfo' in config:
                        game_name = config['Gameinfo']['name']
                        print("Found game:" + game_name)
                        if 'icon' in config['Gameinfo']: 
                            icon_file = game_path + config['Gameinfo']['icon']
                            if not os.path.isfile(icon_file):
                                icon_file = self.assets_dir + '/default_icon.svg'
                        else:
                            icon_file = self.assets_dir + '/default_icon.svg'
                        exec_cmd = "dosbox -conf " + cfg_file
                        game_info = GameInfo(game_name, icon_file)
                        self.add_game_to_list(game_info)
                        self.game_exec.append([game_name, exec_cmd])

    def get_list(self):
        return self.games_list

    def create_dosbox_config(self, mount_path, exec_path, cfg_file):
        if not os.path.isfile(cfg_file) and os.path.isdir(mount_path):
            template = self.assets_dir + '/dosbox.cfg'
            copyfile(template, cfg_file)
            config = configparser.ConfigParser()
            with open(cfg_file, 'a') as f:
                f.write("\n\n[autoexec]\n")
                f.write('MOUNT C ' + mount_path + "\n")
                f.write('C:\n')
                f.write(exec_path)
                f.close()

        return os.path.isfile(cfg_file)


    def add_game_to_list(self, game_info):
        self.games_list.append(game_info.get_row())
        self.games_list_original.append(game_info.get_row())


    def get_original_list(self):
        return self.games_list_original

    def get_exec(self, name):
        for item in self.game_exec:
            if item[0] == name:
                print(item[0])
                return item[1]



