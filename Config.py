import configparser
import os
import pathlib
import platform

class Config:
    config_dir = 'GameDotExe'
    config_file = 'config.ini'

    def __init__(self):
        # Platform-specifieke bepaling van de configuratie map
        if platform.system() == 'Darwin':  # macOS
            config_base = os.path.expanduser('~/Library/Application Support')
        elif platform.system() == 'Windows':
            config_base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        else:  # Linux / Unix
            config_base = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')

        self.config_dir_path = os.path.join(config_base, self.config_dir)
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
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        config['generic'] = {}
        config['generic']['path'] = path
        with open(self.config_file_path, 'w') as configfile:
            config.write(configfile)

    def init_config(self):
        if not self.config_dir_exists():
            os.makedirs(self.config_dir_path, exist_ok=True)
