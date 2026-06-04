import sys
import os
from PySide6.QtWidgets import (QApplication, QFileDialog, QInputDialog)
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QObject, Slot, Property, Signal, QCoreApplication

from Config import Config
from Crawler import Crawler
from GameInfo import GameInfo # Nodig om GameInfo objecten te reconstrueren
from DatabaseManager import DatabaseManager
from MainPresenter import MainPresenter

class QmlBridge(QObject):
    """Bridge klasse om de Presenter met QML te verbinden."""
    gamesChanged = Signal()

    def __init__(self, config, db_manager, crawler):
        super().__init__()
        self.config = config
        self.db_manager = db_manager
        self.crawler = crawler
        self._games = []
        # De presenter heeft nog steeds een 'view' nodig. 
        # We kunnen deze bridge als view laten fungeren.
        self.presenter = MainPresenter(self, self.config, self.db_manager, self.crawler)

    @Property(list, notify=gamesChanged)
    def games(self):
        return self._games

    # --- Implementatie van de View interface voor MainPresenter ---
    def load_games(self, games_list):
        # Converteer GameInfo objecten naar dictionaries voor QML
        self._games = [
            {
                "name": g.name,
                "icon": "file:///" + g.icon_path.replace('\\', '/'),
                "command": g.exec_cmd,
                "folder": g.folder_name,
                "releaseDate": g.release_date or "Unknown",
                "setup_cmd": g.setup_cmd,
                "compatibility": g.compatibility,
                "internal_exec": g.internal_exec,
                "internal_setup": g.internal_setup,
                "iso_path": g.iso_path,
                "icon_path": g.icon_path
            } for g in games_list
        ]
        self.gamesChanged.emit()

    @Slot(str)
    def perform_delete_game(self, folder_name):
        game_info = self.db_manager.get_game(folder_name)
        if game_info:
            self.presenter.delete_game(game_info)
        else:
            self.show_error("Error", f"Game met folder '{folder_name}' niet gevonden voor verwijdering.")

    @Slot(dict)
    def show_edit_game_dialog(self, game_data):
        # Sla de wijzigingen direct op via de presenter (geen QtWidgets dialoog meer)
        game_info = GameInfo(
            folder_name=game_data.get("folder"),
            name=game_data.get("name"),
            icon_path=game_data.get("icon_path"),
            exec_cmd=game_data.get("command"),
            setup_cmd=game_data.get("setup_cmd"),
            compatibility=game_data.get("compatibility", ""),
            release_date=game_data.get("releaseDate", ""),
            internal_exec=game_data.get("internal_exec", ""),
            internal_setup=game_data.get("internal_setup", None),
            iso_path=game_data.get("iso_path", None)
        )
        self.presenter.update_game_properties(game_info, game_data.get("folder"))

    @Slot(str, result=str)
    def browse_executable(self, folder_name):
        game_path = os.path.join(self.config.get_path(), folder_name)
        file_path, _ = QFileDialog.getOpenFileName(None, "Select Executable", game_path, "Executables (*.exe *.com *.bat)")
        if file_path:
            try:
                return os.path.relpath(file_path, game_path).replace('/', '\\')
            except ValueError:
                return file_path
        return ""

    @Slot(result=str)
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select Artwork", "", "Images (*.png *.jpg *.jpeg *.svg)")
        return file_path if file_path else ""

    # --- Benodigde interface methodes voor de Presenter ---
    def prompt_metadata_selection(self, game_name, matches):
        item, ok = QInputDialog.getItem(
            None,
            QCoreApplication.translate("QmlBridge", "Select Metadata Match"),
            QCoreApplication.translate("QmlBridge", "Multiple matches found for '{0}'. Select the correct one:").format(game_name),
            matches,
            0,
            False
        )
        return item if ok else matches[0]

    def prompt_exe_selection(self, game_path):
        file_path, _ = QFileDialog.getOpenFileName(
            None, f"Select main executable in {os.path.basename(game_path)}", 
            game_path, "Executables (*.exe *.com *.bat)"
        )
        if file_path:
            return os.path.relpath(file_path, game_path).replace('/', '\\')
        return None

    def apply_filter(self, text_lower):
        # Filter de lijst van de crawler en update de view
        all_games = self.crawler.get_list()
        filtered_games = [g for g in all_games if text_lower in g.name.lower()]
        self.load_games(filtered_games)

    def show_progress(self, message): pass
    def hide_progress(self): pass
    def show_info(self, title, message): pass
    def show_error(self, title, message): print(f"Error: {message}")

    @Slot(str)
    def launch_game(self, cmd):
        import subprocess
        import shlex
        try:
            if os.name == 'nt':
                subprocess.Popen(cmd, shell=True)
            else:
                args = shlex.split(cmd)
                subprocess.Popen(args)
        except Exception as e:
            print(f"Launch Error: {e}")

    @Slot()
    def start_iso_install(self):
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        iso_path, _ = QFileDialog.getOpenFileName(None, "Select ISO File", "", "ISO Files (*.iso)")
        if not iso_path:
            return
            
        game_name, ok = QInputDialog.getText(None, "Game Name", "Under what name should the game be installed?")
        if ok and game_name:
            self.presenter.install_from_iso(iso_path, game_name)

    @Slot()
    def force_scan(self):
        self.presenter.force_scan()

    @Slot(str)
    def filter_games(self, text):
        self.presenter.filter_games(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/default_icon.svg"))

    config = Config()
    db_path = os.path.join(config.config_dir_path, "games.db")
    db_manager = DatabaseManager(db_path)
    artwork_path = os.path.join(config.config_dir_path, "artwork")
    crawler = Crawler(config.get_path(), db_manager, artwork_dir=artwork_path, log_path=config.get_log_path())

    bridge = QmlBridge(config, db_manager, crawler)

    engine = QQmlApplicationEngine()
    # Maak de bridge beschikbaar in QML
    engine.rootContext().setContextProperty("bridge", bridge)
    engine._bridge = bridge  # Voorkom Garbage Collection van het bridge object
    
    # Bepaal de basispad voor resources, afhankelijk van of het een PyInstaller bundle is
    if getattr(sys, 'frozen', False):
        # Draait in een PyInstaller bundle
        application_base_path = sys._MEIPASS
    else:
        # Draait in een normale Python omgeving
        application_base_path = os.path.dirname(os.path.abspath(__file__))
    engine.rootContext().setContextProperty("applicationBasePath", application_base_path)

    # Laad het QML bestand
    qml_file = os.path.join(application_base_path, "ui", "main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    # Initiële load
    bridge.presenter.initial_load()

    sys.exit(app.exec())
