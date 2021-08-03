import configparser
import os
from pathlib import Path

from xdg import xdg_config_home
from Dialog import Dialog

class Config:
    config_dir = 'GameDotExe'
    config_path = ''
    config_file = 'config.ini'
    config_dir_path = ''
    config_file_path = ''

    def __init__(self):
        self.config_dir_path = os.path.join(xdg_config_home(), self.config_dir)
        self.config_file_path = os.path.join(self.config_dir_path, self.config_file)
        self.init_config()


    def config_dir_exists(self):
        return os.path.isdir(self.config_dir_path)

    def config_file_exists(self):
        return os.path.isfile(self.config_file_path)

    def get_path(self):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        print(self.config_file_path)
        if config.has_section('generic'):
            return config.get('generic', 'path')

    def set_path(self, path):
        filehandler = Path(self.config_file_path)
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        config['generic'] = {}
        config['generic']['path'] = path
        config.write(filehandler.open('w'))

    def init_config(self):
        if not self.config_dir_exists():
            os.mkdir(self.config_dir_path)

        if not self.config_file_exists():
            dialog = Dialog()
            games_path = dialog.select_game_folder()
            self.set_path(games_path)
            dialog.dialog.destroy()
