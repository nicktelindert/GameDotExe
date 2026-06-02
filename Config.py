import configparser
import os
from pathlib import Path
from PySide6.QtWidgets import QFileDialog

class Config:
    config_dir = 'GameDotExe'
    config_file = 'config.ini'

    def __init__(self):
        # Handmatige bepaling van XDG_CONFIG_HOME voor maximale compatibiliteit
        xdg_home = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
        self.config_dir_path = os.path.join(xdg_home, self.config_dir)
        self.config_file_path = os.path.join(self.config_dir_path, self.config_file)
        self.log_file_path = os.path.join(self.config_dir_path, 'pcgamingwiki.log')
        self.init_config()


    def config_dir_exists(self):
        return os.path.isdir(self.config_dir_path)

    def config_file_exists(self):
        return os.path.isfile(self.config_file_path)

    def get_path(self):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        if config.has_section('generic'):
            return config.get('generic', 'path')

    def get_language(self):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        if config.has_section('generic'):
            return config.get('generic', 'language', fallback=None)
        return None

    def get_log_path(self):
        return self.log_file_path

    def set_path(self, path):
        filehandler = Path(self.config_file_path)
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        config['generic'] = {}
        config['generic']['path'] = path
        config.write(filehandler.open('w'))

    def init_config(self):
        if not self.config_dir_exists():
            os.makedirs(self.config_dir_path, exist_ok=True)

        if not self.config_file_exists():
            games_path = QFileDialog.getExistingDirectory(
                None, 
                "Selecteer de map met MS-DOS Games",
                options=QFileDialog.ShowDirsOnly
            )
            if games_path:
                self.set_path(games_path)
