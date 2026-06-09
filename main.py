import sys
import os
import platform
import shutil
from PySide6.QtWidgets import (QApplication, QFileDialog, QInputDialog, QMessageBox)
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtCore import Qt, QObject, Slot, Property, Signal, QCoreApplication, QUrl

from core.Config import Config
from crawlers.Crawler import Crawler
from core.GameInfo import GameInfo # Nodig om GameInfo objecten te reconstrueren
from core.DatabaseManager import DatabaseManager
from presenters.MainPresenter import MainPresenter

class QmlBridge(QObject):
    """Bridge klasse om de Presenter met QML te verbinden."""
    gamesChanged = Signal()
    progressVisibleChanged = Signal()
    progressValueChanged = Signal()
    progressMessageChanged = Signal()

    def __init__(self, config, db_manager, crawler):
        super().__init__()
        self.config = config
        self.db_manager = db_manager
        self.crawler = crawler
        self._games = []
        self._progress_visible = False
        self._progress_value = 0.0
        self._progress_message = ""
        self.presenter = MainPresenter(self, self.config, self.db_manager, self.crawler)

    @Property(list, notify=gamesChanged)
    def games(self):
        return self._games

    @Property(bool, notify=progressVisibleChanged)
    def progressVisible(self): return self._progress_visible

    @Property(float, notify=progressValueChanged)
    def progressValue(self): return self._progress_value

    @Property(str, notify=progressMessageChanged)
    def progressMessage(self): return self._progress_message

    # --- Implementatie van de View interface voor MainPresenter ---
    def load_games(self, games_list):
        # Converteer GameInfo objecten naar dictionaries voor QML
        self._games = [
            {
                "name": g.name,
                "icon": ("file:///" + g.icon_path.replace('\\', '/')) if g.icon_path else "",
                "command": g.exec_cmd or "",
                "folder": g.folder_name,
                "safeFolder": g.safe_folder_name,
                "releaseDate": g.release_date or QCoreApplication.translate("QmlBridge", "Unknown"),
                "setup_cmd": g.setup_cmd,
                "compatibility": g.compatibility,
                "internal_exec": g.internal_exec,
                "internal_setup": g.internal_setup,
                "iso_path": g.iso_path,
                "icon_path": g.icon_path,
                "isIgnored": bool(getattr(g, "is_ignored", False))
            } for g in games_list
        ]
        self.gamesChanged.emit()

    @Slot(str)
    def perform_delete_game(self, folder_name):
        game_info = self.db_manager.get_game(folder_name)
        if game_info:
            self.presenter.delete_game(game_info)
        else:
            self.show_error(QCoreApplication.translate("QmlBridge", "Error"), 
                            QCoreApplication.translate("QmlBridge", "Game folder '{0}' not found for deletion.").format(folder_name))

    @Slot(dict)
    def save_game_properties(self, game_data):
        """Slaat de gewijzigde metadata op via de presenter."""
        game_info = GameInfo(
            folder_name=game_data.get("folder"),
            name=game_data.get("name"),
            icon_path=game_data.get("icon_path"),
            exec_cmd=game_data.get("command"),
            setup_cmd=game_data.get("setup_cmd", None),
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
        manual_option = QCoreApplication.translate("QmlBridge", "[ Manual Entry... ]")
        matches_list = list(matches) if matches else []
        display_list = matches_list + [manual_option]
        
        title = QCoreApplication.translate("QmlBridge", "Select Metadata Match")
        label = QCoreApplication.translate("QmlBridge", "Select the correct match for '{0}':").format(game_name) if matches_list else \
                QCoreApplication.translate("QmlBridge", "No matches found for '{0}'. Enter name manually:").format(game_name)

        item, ok = QInputDialog.getItem(
            None, title, label, display_list,
            len(display_list) - 1 if not matches_list else 0,
            False
        )

        if ok:
            if item == manual_option:
                custom_name, ok_text = QInputDialog.getText(
                    None, QCoreApplication.translate("QmlBridge", "Manual Entry"),
                    QCoreApplication.translate("QmlBridge", "Enter the exact game name for metadata lookup:"),
                    text=game_name
                )
                return custom_name if ok_text and custom_name else game_name
            return item
        return matches_list[0] if matches_list else game_name

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

    def show_progress(self, message):
        self._progress_message = message
        self._progress_visible = True
        self.progressMessageChanged.emit()
        self.progressVisibleChanged.emit()
        QApplication.processEvents() # Forceer UI update

    def set_progress(self, value):
        self._progress_value = value
        self.progressValueChanged.emit()
        QApplication.processEvents() # Forceer UI update

    def hide_progress(self):
        self._progress_visible = False
        self.progressVisibleChanged.emit()

    def show_info(self, title, message): pass

    def show_error(self, title, message):
        """Toon een foutmelding die zichtbaar is voor de gebruiker."""
        QMessageBox.critical(None, title, message)

    @Slot(str)
    def launch_game(self, cmd):
        """Delegeert de launch logica naar de presenter."""
        self.presenter.launch_game(cmd)
    
    @Slot()
    def start_iso_install(self):
        """Delegeert installatie naar de presenter."""
        # De QFileDialog kan hier blijven of via de presenter aangeroepen worden
        iso_path, _ = QFileDialog.getOpenFileName(None, QCoreApplication.translate("QmlBridge", "Select Disk Image"), "", "Disk Images (*.iso *.cue *.bin)")
        if not iso_path: return

        game_name, ok = QInputDialog.getText(None, 
            QCoreApplication.translate("QmlBridge", "Install Game"), 
            QCoreApplication.translate("QmlBridge", "Under what name should the game be installed?\n\n(Important: During setup, install the files directly to C:\\)")
        )
        if ok and game_name:
            self.presenter.install_from_iso(iso_path, game_name)

    @Slot()
    @Slot(str)
    def force_scan(self, folder=None):
        self.presenter.force_scan(folder)

    @Slot(str)
    def filter_games(self, text):
        self.presenter.filter_games(text)

    @Slot(str)
    def ignore_folder(self, folder_name):
        self.presenter.ignore_folder(folder_name)

    @Slot(str)
    def unignore_folder(self, folder_name):
        self.presenter.unignore_folder(folder_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QQuickStyle.setStyle("Fusion")
    app.setApplicationName("GameDotExe")
    app.setOrganizationName("GameDotExe")
    app.setOrganizationDomain("gamedotexe.org")
    config = Config()

    # Controleer of er een geldige bibliotheekmap is ingesteld (vooral belangrijk bij de eerste start)
    library_path = config.get_path()
    if not library_path or not os.path.exists(library_path):
        library_path = QFileDialog.getExistingDirectory(
            None, 
            QCoreApplication.translate("main", "Select the folder where your DOS games are located"),
            os.path.expanduser("~")
        )
        if library_path:
            config.set_path(library_path)
        else:
            # Zonder een bibliotheekmap kan de launcher niet functioneren
            sys.exit(0)

    db_path = os.path.join(config.config_dir_path, "games.db")
    db_manager = DatabaseManager(db_path)
    artwork_path = os.path.join(config.config_dir_path, "artwork")
    crawler = Crawler(config.get_path(), db_manager, artwork_dir=artwork_path, log_path=config.get_log_path())

    bridge = QmlBridge(config, db_manager, crawler)

    # Registreer de Bridge als een Singleton voor QML
    # Gebruik een URI (bijv. "GameDotExe") en een versie
    qmlRegisterSingletonInstance(QmlBridge, "GameDotExe", 1,0, "Bridge", bridge)

    engine = QQmlApplicationEngine()
    
    # Bepaal de basispad voor resources, afhankelijk van of het een PyInstaller bundle is
    if getattr(sys, 'frozen', False):
        # Draait in een PyInstaller bundle
        application_base_path = sys._MEIPASS
    else:
        # Draait in een normale Python omgeving
        application_base_path = os.path.dirname(os.path.abspath(__file__))
    engine.rootContext().setContextProperty("applicationBasePath", application_base_path)

    # Stel het icon pad correct in t.o.v. de bundle root om runtime errors te voorkomen
    app.setWindowIcon(QIcon(os.path.join(application_base_path, "assets", "default_icon.svg")))

    # Laad het QML bestand uit de views map
    qml_file = os.path.join(application_base_path, "views", "main.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    # Initiële load
    bridge.presenter.initial_load()

    exit_code = app.exec()
    
    # Forceer opruimen engine voor Bridge om null-pointer errors in QML te voorkomen
    del engine
    db_manager.close()
    sys.exit(exit_code)
