from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QCoreApplication

class AboutDialog(QDialog):
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