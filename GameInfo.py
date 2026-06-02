from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication

class GameInfo:
    def __init__(self, folder_name, name, icon_path, exec_cmd=None, setup_cmd=None, compatibility=None, release_date=None, internal_exec=None, internal_setup=None):
        # Gebruik vertaalbare defaults
        default_str = QCoreApplication.translate("GameInfo", "Onbekend")
        
        self.folder_name = folder_name
        self.name = name
        self.icon_path = icon_path
        self.exec_cmd = exec_cmd
        self.setup_cmd = setup_cmd
        self.compatibility = compatibility or default_str
        self.release_date = release_date or default_str
        self.internal_exec = internal_exec
        self.internal_setup = internal_setup

    def get_icon(self):
        try:
            return QIcon(self.icon_path)
        except:
            return QIcon()