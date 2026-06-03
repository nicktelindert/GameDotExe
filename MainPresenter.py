import os
import shutil

class MainPresenter:
    def __init__(self, view, config, db_manager, crawler):
        self.view = view
        self.config = config
        self.db = db_manager
        self.crawler = crawler

    def initial_load(self):
        """Eerste scan bij opstarten."""
        self.crawler.build_list(
            selection_callback=self.view.prompt_metadata_selection,
            exe_selection_callback=self.view.prompt_exe_selection
        )
        self.view.load_games(self.crawler.get_list())

    def force_scan(self, target_folder=None):
        """Handmatige herscan van de library."""
        self.view.show_progress("Scanning library...")
        self.crawler.build_list(
            force_scan=True,
            selection_callback=self.view.prompt_metadata_selection,
            exe_selection_callback=self.view.prompt_exe_selection,
            target_folder=target_folder
        )
        self.view.load_games(self.crawler.get_list())
        self.view.hide_progress()

    def filter_games(self, search_text):
        """Filter de lijst op basis van zoekterm."""
        self.view.apply_filter(search_text.lower())

    def install_gog_game(self, installer_path, game_name):
        """Beheer de GOG installatie flow."""
        from GogInstaller import GogInstaller
        self.view.show_progress("Installing and scanning game...")
        try:
            installer = GogInstaller(self.config.get_path())
            installer.install(installer_path, game_name)
            
            # Scan alleen de nieuwe folder
            self.crawler.build_list(
                force_scan=False,
                selection_callback=self.view.prompt_metadata_selection,
                exe_selection_callback=self.view.prompt_exe_selection
            )
            self.view.load_games(self.crawler.get_list())
            self.view.show_info("Done", f"{game_name} has been successfully imported.")
        except Exception as e:
            self.view.show_error("Error", str(e))
        finally:
            self.view.hide_progress()

    def delete_game(self, game_info):
        """Verwijder een game van schijf en uit DB."""
        if self.view.confirm_deletion(game_info.name):
            # 1. Verwijder uit database
            self.db.delete_game(game_info.folder_name)
            # 2. Verwijder map van schijf
            game_path = os.path.join(self.config.get_path(), game_info.folder_name)
            if os.path.exists(game_path):
                shutil.rmtree(game_path)
            # 3. Ververs lijst
            self.crawler.build_list()
            self.view.load_games(self.crawler.get_list())

    def update_game_properties(self, game_info, old_folder_name):
        """Slaat gewijzigde metadata op en ververst de UI."""
        game_path = os.path.join(self.config.get_path(), old_folder_name)
        
        # Update configs op schijf
        self.crawler.create_dosbox_config(game_path, game_info.internal_exec, os.path.join(game_path, "dosbox.cfg"))
        if game_info.internal_setup:
            self.crawler.create_dosbox_config(game_path, game_info.internal_setup, os.path.join(game_path, "dosbox_setup.cfg"))
        
        # Update Database
        self.db.save_game(old_folder_name, game_info)
        
        # Reload UI
        self.view.load_games(self.crawler.get_list())