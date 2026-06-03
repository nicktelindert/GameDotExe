from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QCoreApplication

class GameWidget(QWidget):
    def __init__(self, game_info, launch_callback, parent=None):
        super().__init__(parent)
        self.game_info = game_info
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Icon
        icon_label = QLabel()
        icon = QIcon(self.game_info.icon_path)
        icon_label.setPixmap(icon.pixmap(128, 128))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Naam
        name_label = QLabel(game_info.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # Release Datum
        release_val = game_info.release_date or QCoreApplication.translate('GameWidget', 'Unknown')
        date_label = QLabel(f"{QCoreApplication.translate('GameWidget', 'Released')}: {release_val}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(date_label)

        # Knoppen
        btn_layout = QHBoxLayout()
        play_btn = QPushButton(QCoreApplication.translate("GameWidget", "Play"))
        play_btn.clicked.connect(lambda: launch_callback(game_info.exec_cmd))
        btn_layout.addWidget(play_btn)

        layout.addLayout(btn_layout)