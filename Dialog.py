from PySide6.QtWidgets import QFileDialog

class Dialog:
    def select_game_folder(self):
        folder = QFileDialog.getExistingDirectory(
            None, 
            "Selecteer de map met MS-DOS Games",
            options=QFileDialog.ShowDirsOnly
        )
        return folder
