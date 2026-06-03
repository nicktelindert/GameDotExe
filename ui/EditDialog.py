from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import QCoreApplication

class EditDialog(QDialog):
    def __init__(self, game_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{QCoreApplication.translate('EditDialog', 'Edit Properties')}: {game_info.name}")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)

        # UI Velden
        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Game Name:")))
        self.name_edit = QLineEdit(game_info.name)
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Internal Game Executable (e.g., START.EXE):")))
        self.exec_edit = QLineEdit(game_info.internal_exec or "")
        layout.addWidget(self.exec_edit)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Internal Setup Executable (e.g., SETUP.EXE):")))
        self.setup_edit = QLineEdit(game_info.internal_setup or "")
        layout.addWidget(self.setup_edit)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Release Date:")))
        self.release_edit = QLineEdit(game_info.release_date or "")
        layout.addWidget(self.release_edit)

        layout.addWidget(QLabel(QCoreApplication.translate("EditDialog", "Artwork Path:")))
        art_layout = QHBoxLayout()
        self.art_edit = QLineEdit(game_info.icon_path or "")
        art_layout.addWidget(self.art_edit)
        browse_btn = QPushButton(QCoreApplication.translate("EditDialog", "Browse..."))
        browse_btn.clicked.connect(self.browse_artwork)
        art_layout.addWidget(browse_btn)
        layout.addLayout(art_layout)

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

    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'exec': self.exec_edit.text(),
            'setup': self.setup_edit.text(),
            'release_date': self.release_edit.text(),
            'icon_path': self.art_edit.text()
        }

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)