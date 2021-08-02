import os

import gi
import xdg
import configparser
gi.require_version('GdkPixbuf', '2.0')
gi.require_version("Gtk", "3.0")
from gi.repository.GdkPixbuf import Pixbuf

from gameinfo import gameInfo

games_list = []
from gi.repository import Gtk
from xdg import (
    xdg_config_home,
)

title = "GameDotExe"
version = "0.1"

def detectgames(games_path):
    print("Found game path:" + games_path)
    print("Search directories in " + games_path)
    print(os.listdir(games_path))
    for game in os.listdir(games_path):
        game_path = games_path + '/' + game + '/';
        ini_file = game_path + game + '.ini'
        cfg_file = game_path + 'dosbox.cfg'
        config = configparser.ConfigParser()
        config.read(ini_file)
        exec_path = config['Gameinfo']['exec']
        print(exec_path);
        if not os.path.isfile(cfg_file):
            config = configparser.ConfigParser()
            with open(cfg_file, 'a') as f:
                f.write("[autoexec]\n")
                f.write('MOUNT C ' + game_path+"data/\n")
                f.write('C:\n')
                f.write(exec_path)
                f.close()

        if (os.path.isfile(ini_file) and os.path.isfile(cfg_file)):
            config = configparser.ConfigParser()
            config.read(ini_file)
            game_name = config['Gameinfo']['name']
            print("Found game:" + game_name)
            icon_file = game_path + config['Gameinfo']['icon']
            exec_cmd = "dosbox -conf " + cfg_file;
            game_info = gameInfo(game_name, exec_cmd, icon_file)
            games_list.append(game_info)


def initialize():
    folder = 'dosgames'
    config_path = os.path.join(xdg_config_home(), folder)
    print(xdg_config_home())
    if not os.path.isdir(config_path):
        os.mkdir(config_path)
        dialog = Gtk.FileChooserDialog(
            title="Choose game folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            config = configparser.ConfigParser()
            configfile = os.path.join(config_path, 'config.ini')
            with open(configfile, 'w') as configfile:
                config.write(configfile)
                config['generic'] = {}
                config['generic']['path'] = dialog.get_filename()
                config.write(configfile)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


def run_game(widget, cmd):
    os.system(cmd)


def main():
    folder = 'dosgames'
    config_path = os.path.join(xdg_config_home(), folder)
    configfile = os.path.join(config_path, 'config.ini')
    config = configparser.ConfigParser()
    config.read(configfile)
    games_path = config['generic']['path']

    win = Gtk.Window()
    win.set_title(title + " " + version)
    win.connect("destroy", Gtk.main_quit)
    win.set_resizable(False)
    detectgames(games_path)
    box = Gtk.VBox()
    label = Gtk.Label("Games")
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
            button.set_always_show_image (True)

        button.connect("clicked", run_game, game.exec)
        box.pack_start(button, True, True, 0)
    win.add(box)
    win.show_all()
    Gtk.main()


initialize()
main()
