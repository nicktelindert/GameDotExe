import os

class EditPresenter:
    def __init__(self, view, game_info, config, db_manager, main_presenter):
        self.view = view
        self.game_info = game_info
        self.config = config
        self.db = db_manager
        self.main_presenter = main_presenter

    def save_changes(self, new_data):
        old_folder_name = self.game_info.folder_name
        new_name = new_data['name']

        # Update de data in het object
        self.game_info.name = new_name
        self.game_info.internal_exec = new_data['exec']
        self.game_info.internal_setup = new_data['setup']
        self.game_info.release_date = new_data['release_date']
        self.game_info.icon_path = new_data['icon_path']

        if new_name != old_folder_name:
            # Map hernoemen logica
            old_path = os.path.join(self.config.get_path(), old_folder_name)
            new_path = os.path.join(self.config.get_path(), new_name)
            
            if os.path.exists(new_path):
                self.view.show_error("Error", "A folder with this name already exists.")
                return False
            
            try:
                os.rename(old_path, new_path)
                # Update database (verwijder oud, scan nieuw)
                self.db.delete_game(old_folder_name)
                self.main_presenter.force_scan(target_folder=new_name)
                return True
            except Exception as e:
                self.view.show_error("Error", f"Failed to rename folder: {str(e)}")
                return False
        else:
            # Alleen properties updaten
            self.main_presenter.update_game_properties(self.game_info, old_folder_name)
            return True