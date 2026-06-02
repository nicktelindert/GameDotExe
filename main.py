import sys
import os
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidget, 
                             QListWidgetItem, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QLabel, QPushButton, QDialog, 
                             QListWidget as QListSelection, QFileDialog, QInputDialog, QMessageBox,
                             QMenu, QProgressDialog)
from PySide6.QtCore import Qt, QSize, QTranslator, QLocale, QLibraryInfo, QCoreApplication
from PySide6.QtGui import QAction
from Config import Config
from Crawler import Crawler
from DatabaseManager import DatabaseManager
from GogInstaller import GogInstaller

class AboutDialog(QDialog):
    """Dialoogvenster met informatie over de applicatie."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(QCoreApplication.translate("AboutDialog", "About GameDotExe"))
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        title = QLabel("<h2>GameDotExe</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel(QCoreApplication.translate("AboutDialog", "Version 1.0.0"))
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        credits = QLabel(
            QCoreApplication.translate("AboutDialog", "<p>A modern DOSBox game launcher built with Python and Qt6.</p><p><b>Credits:</b></p>") +
            "<ul>"
            f"<li>{QCoreApplication.translate('AboutDialog', 'Developed by Nick te Lindert')}</li>"
            f"<li>{QCoreApplication.translate('AboutDialog', 'Metadata via PCGamingWiki')}</li>"
            f"<li>{QCoreApplication.translate('AboutDialog', 'DOS emulation by DOSBox')}</li>"
            f"<li>{QCoreApplication.translate('AboutDialog', 'GOG extraction via innoextract')}</li>"
            "</ul>"
        )
        credits.setWordWrap(True)
        layout.addWidget(credits)

        close_btn = QPushButton(QCoreApplication.translate("AboutDialog", "Close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class EditDialog(QDialog):
    """Dialoogvenster om game-eigenschappen te bewerken."""
    def __init__(self, game_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{QCoreApplication.translate('EditDialog', 'Edit Properties')}: {game_info.name}")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)

        # Naam
        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Game Name:")))
        self.name_edit = QLineEdit(game_info.name)
        layout.addWidget(self.name_edit)
        layout.addSpacing(10)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Internal Game Executable (e.g., START.EXE):")))
        self.exec_edit = QLineEdit(game_info.internal_exec or "")
        layout.addWidget(self.exec_edit)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Internal Setup Executable (e.g., SETUP.EXE):")))
        self.setup_edit = QLineEdit(game_info.internal_setup or "")
        layout.addWidget(self.setup_edit)

        # Release Date
        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Release Date:")))
        self.release_edit = QLineEdit(game_info.release_date or "")
        layout.addWidget(self.release_edit)

        # Artwork Path
        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Artwork Path:")))
        art_layout = QHBoxLayout()
        self.art_edit = QLineEdit(game_info.icon_path or "")
        art_layout.addWidget(self.art_edit)
        browse_btn = QPushButton(QCoreApplication.translate("EditDialog", "Browse..."))
        browse_btn.clicked.connect(self.browse_artwork)
        art_layout.addWidget(browse_btn)
        layout.addLayout(art_layout)

        layout.addSpacing(20)

        # Buttons
        btns = QHBoxLayout()
        save_btn = QPushButton(QCoreApplication.translate("EditDialog", "Save"))
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(QCoreApplication.translate("EditDialog", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def browse_artwork(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, QCoreApplication.translate("EditDialog", "Select Artwork"), 
            "", QCoreApplication.translate("EditDialog", "Images (*.png *.jpg *.jpeg *.svg)")
        )
        if file_path:
            self.art_edit.setText(file_path)

class GameWidget(QWidget):
    """Custom widget voor een game item in de lijst."""
    def __init__(self, game_info, launch_callback, parent=None):
        super().__init__(parent)
        self.game_info = game_info
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(game_info.get_icon().pixmap(128, 128))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Naam
        name_label = QLabel(game_info.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # Release Datum
        date_label = QLabel(f"{QCoreApplication.translate('GameWidget', 'Released')}: {game_info.release_date}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(date_label)

        # Knoppen
        btn_layout = QHBoxLayout()
        play_btn = QPushButton(QCoreApplication.translate("GameWidget", "Play"))
        play_btn.clicked.connect(lambda: launch_callback(game_info.exec_cmd))
        btn_layout.addWidget(play_btn)

        
        layout.addLayout(btn_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "GameDotExe - DOSBox Launcher"))
        self.setMinimumSize(900, 700)
        
        self.config = Config()
        db_path = os.path.join(self.config.config_dir_path, "games.db")
        self.db_manager = DatabaseManager(db_path)
        
        # Maak een pad voor de lokale artwork cache
        artwork_path = os.path.join(self.config.config_dir_path, "artwork")
        self.crawler = Crawler(self.config.get_path(), self.db_manager, artwork_dir=artwork_path, log_path=self.config.get_log_path())
        self.crawler.build_list(selection_callback=self.prompt_metadata_selection, exe_selection_callback=self.prompt_exe_selection)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Top bar
        top_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(QCoreApplication.translate("MainWindow", "Search for a game..."))
        self.search_bar.textChanged.connect(self.filter_games)
        top_layout.addWidget(self.search_bar)

        self.force_scan_btn = QPushButton(QCoreApplication.translate("MainWindow", "Force Scan"))
        self.force_scan_btn.clicked.connect(self.force_scan)
        top_layout.addWidget(self.force_scan_btn)

        self.gog_install_btn = QPushButton(QCoreApplication.translate("MainWindow", "Install from GOG"))
        self.gog_install_btn.clicked.connect(self.install_gog_game)
        top_layout.addWidget(self.gog_install_btn)

        self.about_btn = QPushButton(QCoreApplication.translate("MainWindow", "About"))
        self.about_btn.clicked.connect(self.show_about_dialog)
        top_layout.addWidget(self.about_btn)
        
        self.layout.addLayout(top_layout)
        
        # Game Lijst
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSpacing(20)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.list_widget)
        
        self.load_games()

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def prompt_metadata_selection(self, game_name, matches):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{QCoreApplication.translate('MainWindow', 'Select metadata for')}: {game_name}")
        layout = QVBoxLayout(dialog)
        list_widget = QListSelection()
        list_widget.addItems(matches)
        layout.addWidget(list_widget)
        btn = QPushButton(QCoreApplication.translate("MainWindow", "Select"))
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        if dialog.exec() == QDialog.Accepted:
            return list_widget.currentItem().text()
        return game_name

    def prompt_exe_selection(self, game_path):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"{QCoreApplication.translate('MainWindow', 'Select startup file for')}: {os.path.basename(game_path)}", 
            game_path, 
            QCoreApplication.translate("MainWindow", "Executables (*.exe *.com *.bat)")
        )
        if file_path:
            return os.path.relpath(file_path, game_path).replace('/', '\\')
        return None

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        game = item.data(Qt.UserRole)
        menu = QMenu(self)
        
        # Setup actie (alleen als setup_cmd bestaat)
        if game.setup_cmd:
            setup_action = QAction(QCoreApplication.translate("MainWindow", "Run Setup"), self)
            setup_action.triggered.connect(lambda: self.launch_cmd(game.setup_cmd))
            menu.addAction(setup_action)
            menu.addSeparator()
            
        # Bewerken
        edit_action = QAction(QCoreApplication.translate("MainWindow", "Edit Properties"), self)
        edit_action.triggered.connect(lambda: self.edit_game(game))
        menu.addAction(edit_action)
        
        # Verwijderen
        delete_action = QAction(QCoreApplication.translate("MainWindow", "Delete"), self)
        delete_action.triggered.connect(lambda: self.delete_game(game))
        menu.addAction(delete_action)
        
        menu.exec(self.list_widget.mapToGlobal(pos))

    def install_gog_game(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, QCoreApplication.translate("MainWindow", "Select GOG Installer"), 
            "", QCoreApplication.translate("MainWindow", "Executables (*.exe)")
        )
        if not file_path:
            return

        # Probeer een standaard naam te extraheren
        default_name = os.path.splitext(os.path.basename(file_path))[0].replace("setup_", "").split("_")[0].capitalize()
        
        game_name, ok = QInputDialog.getText(
            self, QCoreApplication.translate("MainWindow", "GOG Installation"), 
            QCoreApplication.translate("MainWindow", "Under what name should the game be saved?"),
            QLineEdit.Normal, default_name
        )

        if ok and game_name:
            progress = QProgressDialog(QCoreApplication.translate("MainWindow", "Installing and scanning game..."), None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QApplication.processEvents()
            try:
                installer = GogInstaller(self.config.get_path())
                installer.install(file_path, game_name)
                # Alleen nieuwe games scannen, geen force scan op alles
                self.crawler.build_list(force_scan=False, selection_callback=self.prompt_metadata_selection, exe_selection_callback=self.prompt_exe_selection)
                self.load_games()
                progress.close()
                msg = QCoreApplication.translate("MainWindow", "{0} has been successfully imported.").format(game_name)
                QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Done"), msg)
            except Exception as e:
                progress.close()
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Error"), str(e))

    def edit_game(self, game_info):
        dialog = EditDialog(game_info, self)
        if dialog.exec() == QDialog.Accepted:
            old_folder_name = game_info.folder_name
            new_name = dialog.name_edit.text()
            
            # Update game_info object met nieuwe waarden
            game_info.name = new_name
            game_info.internal_exec = dialog.exec_edit.text()
            game_info.internal_setup = dialog.setup_edit.text()
            game_info.release_date = dialog.release_edit.text()
            game_info.icon_path = dialog.art_edit.text()

            if new_name != old_folder_name:
                # 1. Folder hernoemen op schijf
                old_path = os.path.join(self.config.get_path(), old_folder_name)
                new_path = os.path.join(self.config.get_path(), new_name)
                
                if os.path.exists(new_path):
                    QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Error"), QCoreApplication.translate("MainWindow", "A folder with this name already exists."))
                    return
                
                os.rename(old_path, new_path)
                
                # 2. Oude entry verwijderen
                self.db_manager.delete_game(old_folder_name)
                
                # 3. Nieuwe scan doen op de nieuwe folder
                self.crawler.build_list(force_scan=True, selection_callback=self.prompt_metadata_selection, exe_selection_callback=self.prompt_exe_selection, target_folder=new_name)
            else:
                # Alleen metadata gewijzigd: update configs en DB
                game_path = os.path.join(self.config.get_path(), old_folder_name)
                self.crawler.create_dosbox_config(game_path, game_info.internal_exec, os.path.join(game_path, "dosbox.cfg"))
                if game_info.internal_setup:
                    self.crawler.create_dosbox_config(game_path, game_info.internal_setup, os.path.join(game_path, "dosbox_setup.cfg"))
                
                self.db_manager.save_game(old_folder_name, game_info)
            
            self.load_games()

    def delete_game(self, game_info):
        reply = QMessageBox.question(
            self, QCoreApplication.translate("MainWindow", "Confirm Deletion"),
            QCoreApplication.translate("MainWindow", "Are you sure you want to delete '{0}'?\n\n"
            "This will permanently delete the game from the list and the folder on disk.")
            .format(game_info.name),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 1. Verwijder uit database
            self.db_manager.delete_game(game_info.folder_name)
            # 2. Verwijder map van schijf
            game_path = os.path.join(self.config.get_path(), game_info.folder_name)
            if os.path.exists(game_path):
                shutil.rmtree(game_path)
            # 3. Ververs lijst
            self.crawler.build_list()
            self.load_games()

    def force_scan(self):
        selected_item = self.list_widget.currentItem()
        target = selected_item.data(Qt.UserRole + 1) if selected_item else None
        
        progress = QProgressDialog(QCoreApplication.translate("MainWindow", "Scanning library..."), None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        self.crawler.build_list(
            force_scan=True, 
            selection_callback=self.prompt_metadata_selection,
            exe_selection_callback=self.prompt_exe_selection,
            target_folder=target
        )
        self.load_games()
        progress.close()

    def load_games(self):
        self.list_widget.clear()
        for game in self.crawler.get_list():
            item = QListWidgetItem(self.list_widget)
            item.setText(game.name) # Nodig voor filtering
            
            widget = GameWidget(game, self.launch_cmd)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, game)
            item.setData(Qt.UserRole + 1, game.folder_name)
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def filter_games(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def launch_cmd(self, cmd):
        if cmd:
            os.system(cmd)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialiseer config om taalinstelling te lezen
    config = Config()
    forced_lang = config.get_language()
    
    # --- Vertaling logica ---
    translator = QTranslator()
    translations_path = os.path.join(os.path.dirname(__file__), "translations")
    
    # Gebruik geforceerde taal of systeemtaal
    locale = QLocale(forced_lang) if forced_lang else QLocale.system()
    QLocale.setDefault(locale)

    if translator.load(locale, "gamedotexe", "_", translations_path):
        app.installTranslator(translator)
        
    # Laad ook standaard Qt systeemvertalingen (voor QFileDialog etc)
    qt_translator = QTranslator()
    qt_trans_path = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    if qt_translator.load(QLocale.system(), "qtbase", "_", qt_trans_path):
        app.installTranslator(qt_translator)
    # -----------------------

    # Voor AppImage support en styling
    app.setStyle("Fusion") 
    window = MainWindow() # MainWindow gebruikt nu de al geladen config
    window.show()
    sys.exit(app.exec())
