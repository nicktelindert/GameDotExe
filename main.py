import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, 
                             QDialog, QListWidget as QListSelection, QFileDialog, 
                             QInputDialog, QMessageBox, QMenu, QProgressDialog)
from PySide6.QtCore import Qt, QSize, QTranslator, QLocale, QLibraryInfo, QCoreApplication
from PySide6.QtGui import QAction
from Config import Config
from Crawler import Crawler
from DatabaseManager import DatabaseManager
from MainPresenter import MainPresenter
from EditPresenter import EditPresenter
from ui.AboutDialog import AboutDialog
from ui.EditDialog import EditDialog
from ui.GameWidget import GameWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "GameDotExe - DOSBox Launcher"))
        self.setMinimumSize(900, 700)

        # 1. Initialiseer de infrastructuur
        self.config = Config()
        db_path = os.path.join(self.config.config_dir_path, "games.db")
        self.db_manager = DatabaseManager(db_path)
        artwork_path = os.path.join(self.config.config_dir_path, "artwork")
        self.crawler = Crawler(self.config.get_path(), self.db_manager, artwork_dir=artwork_path, log_path=self.config.get_log_path())

        # 2. De Presenter koppelen aan deze View
        self.presenter = MainPresenter(self, self.config, self.db_manager, self.crawler)

        # 3. UI Opbouw
        self.setup_ui()

        # 4. Start de applicatie logica
        self.presenter.initial_load()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Top bar: Zoeken en Acties
        top_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search for a game..."))
        self.search_bar.textChanged.connect(self.presenter.filter_games)
        top_layout.addWidget(self.search_bar)

        self.force_scan_btn = QPushButton(QCoreApplication.translate("MainWindow", "Force Scan"))
        self.force_scan_btn.clicked.connect(self.handle_force_scan)
        top_layout.addWidget(self.force_scan_btn)

        self.gog_install_btn = QPushButton(QCoreApplication.translate("MainWindow", "Install from GOG"))
        self.gog_install_btn.clicked.connect(self.install_gog_game)
        top_layout.addWidget(self.gog_install_btn)

        self.about_btn = QPushButton(QCoreApplication.translate("MainWindow", "About"))
        self.about_btn.clicked.connect(self.show_about_dialog)
        top_layout.addWidget(self.about_btn)

        self.layout.addLayout(top_layout)

        # De Grid/Lijst met games
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        # Zet view mode op iconen voor een grid-look
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.setWordWrap(True)
        self.layout.addWidget(self.list_widget)

    # --- View Interface Implementatie (gebruikt door Presenter) ---

    def load_games(self, games_list):
        self.list_widget.clear()
        for game in games_list:
            item = QListWidgetItem(self.list_widget)
            item.setText(game.name) # Voor de interne filter-zoekfunctie
            item.setData(Qt.UserRole, game) # Bewaar het info object
            item.setData(Qt.UserRole + 1, game.folder_name)
            item.setSizeHint(QSize(200, 240))
            
            widget = GameWidget(game, self.launch_game)
            self.list_widget.setItemWidget(item, widget)

    def apply_filter(self, text_lower):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text_lower not in item.text().lower())

    def show_progress(self, message):
        self._progress = QProgressDialog(QCoreApplication.translate("MainWindow", message), None, 0, 0, self)
        self._progress.setWindowModality(Qt.WindowModal)
        self._progress.show()
        QApplication.processEvents()

    def hide_progress(self):
        if hasattr(self, '_progress'):
            self._progress.close()

    def show_info(self, title, message):
        QMessageBox.information(self, QCoreApplication.translate("MainWindow", title), message)

    def show_error(self, title, message):
        QMessageBox.critical(self, QCoreApplication.translate("MainWindow", title), message)

    def confirm_deletion(self, name):
        reply = QMessageBox.question(
            self, QCoreApplication.translate("MainWindow", "Confirm Deletion"),
            QCoreApplication.translate("MainWindow", "Are you sure you want to delete '{0}'?\n\n"
            "This will permanently delete the game from the list and the folder on disk.").format(name),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def prompt_metadata_selection(self, game_name, matches):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Select match for {game_name}")
        l = QVBoxLayout(dialog)
        list_sel = QListSelection()
        list_sel.addItems(matches)
        l.addWidget(list_sel)
        btn = QPushButton("Select")
        btn.clicked.connect(dialog.accept)
        l.addWidget(btn)
        if dialog.exec() == QDialog.Accepted:
            return list_sel.currentItem().text()
        return matches[0]

    def prompt_exe_selection(self, game_path):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select main executable in {os.path.basename(game_path)}", 
            game_path, "Executables (*.exe *.com *.bat)"
        )
        if file_path:
            return os.path.relpath(file_path, game_path).replace('/', '\\')
        return None

    # --- Gebruikersacties ---

    def launch_game(self, cmd):
        """Start een game op een OS-agnostische manier."""
        import subprocess
        import shlex
        try:
            if os.name == 'nt':  # Windows
                # Op Windows werkt shell=True vaak beter voor .bat of complexe commando's
                subprocess.Popen(cmd, shell=True)
            else:  # macOS / Linux
                # Op Unix-achtige systemen is het veiliger om de commando's te splitsen
                args = shlex.split(cmd)
                subprocess.Popen(args)
        except Exception as e:
            self.show_error("Launch Error", f"Could not start game: {str(e)}")

    def handle_force_scan(self):
        selected_item = self.list_widget.currentItem()
        target = selected_item.data(Qt.UserRole + 1) if selected_item else None
        self.presenter.force_scan(target_folder=target)

    def install_gog_game(self):
        file_path, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate("MainWindow", "Select GOG Installer"), "", QCoreApplication.translate("MainWindow", "Executables (*.exe)"))
        if not file_path: return
        
        game_name, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "GOG Installation"), QCoreApplication.translate("MainWindow", "Under what name should the game be saved?"))
        if ok and game_name:
            self.presenter.install_gog_game(file_path, game_name)

    def handle_edit_game(self, game_info):
        dialog = EditDialog(game_info, self)
        edit_presenter = EditPresenter(dialog, game_info, self.config, self.db_manager, self.presenter)
        if dialog.exec() == QDialog.Accepted:
            edit_presenter.save_changes(dialog.get_data())

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item: return
        game = item.data(Qt.UserRole)
        menu = QMenu()
        edit_action = menu.addAction("Edit Properties")
        edit_action.triggered.connect(lambda: self.handle_edit_game(game))
        del_action = menu.addAction("Delete")
        del_action.triggered.connect(lambda: self.presenter.delete_game(game))
        menu.exec(self.list_widget.mapToGlobal(pos))

    def show_about_dialog(self):
        AboutDialog(self).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
