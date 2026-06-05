import os
import shutil
import sys
from PySide6.QtCore import QCoreApplication

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

    def install_from_iso(self, iso_path, game_name):
        """Start de installatie van een game vanaf een ISO."""
        self.view.show_progress("Preparing installation...")
        try:
            game_path = os.path.join(self.config.get_path(), game_name)
            if os.path.exists(game_path):
                raise Exception(QCoreApplication.translate("MainPresenter", "The folder '{0}' already exists.").format(game_name))

            os.makedirs(game_path, exist_ok=True)

            # Maak een tijdelijke DOSBox config om de installer te draaien
            cfg_file = os.path.join(game_path, "install_dosbox.cfg")
            with open(cfg_file, 'w') as f:
                f.write("[sdl]\n[autoexec]\n")
                f.write(f"MOUNT C \"{game_path}\"\n")
                f.write(f"IMGMOUNT D \"{iso_path}\" -t iso\n")
                f.write("D:\n")
                f.write("autorun.bat\n")
                # Probeer setup of install
                f.write("setup.exe\n")
                f.write("setup.bat\n")
                
                f.write("install.exe\n")
                f.write("install.bat\n")

                f.write("PAUSE\n")
                f.write("EXIT\n")

            # Start DOSBox interactief
            # Zoek naar gebundelde dosbox
            bundled_dosbox = os.path.join(getattr(sys, '_MEIPASS', ''), 'dosbox')
            dosbox_cmd = bundled_dosbox if os.path.exists(bundled_dosbox) else "dosbox"
            
            if not shutil.which(dosbox_cmd) and not os.path.exists(bundled_dosbox):
                 raise Exception(QCoreApplication.translate("MainPresenter", "DOSBox binary not found."))

            import subprocess
            subprocess.run([dosbox_cmd, "-conf", cfg_file])

            # Ruim tijdelijke config op
            if os.path.exists(cfg_file):
                os.remove(cfg_file)

            # Scan de library om de nieuwe game te detecteren
            self.force_scan()
            # Na de scan, haal de game op uit de DB en update de iso_path.
            game_info = self.db.get_game(game_name)
            if game_info:
                # Stel de iso_path in op het GameInfo object
                game_info.iso_path = iso_path
                self.db.save_game(game_name, game_info) # Sla het bijgewerkte GameInfo object op
                self.view.load_games(self.crawler.get_list()) # Ververs de UI
            else:
                self.view.show_error(QCoreApplication.translate("MainPresenter", "Error"), 
                                     QCoreApplication.translate("MainPresenter", "Could not find '{0}' after installation scan.").format(game_name))

        except Exception as e:
            self.view.show_error("Error", str(e))
        finally:
            self.view.hide_progress()

    def delete_game(self, game_info): # Deze methode wordt nu aangeroepen *na* bevestiging vanuit QML
        """Verwijder een game van schijf en uit DB."""
        # 1. Verwijder uit database
        self.db.delete_game(game_info.folder_name)
        # 2. Verwijder map van schijf
        game_path = os.path.join(self.config.get_path(), game_info.folder_name)
        if os.path.exists(game_path):
            shutil.rmtree(game_path)
        # 3. Ververs lijst
        self.crawler.build_list(
            selection_callback=self.view.prompt_metadata_selection,
            exe_selection_callback=self.view.prompt_exe_selection
        )
        self.view.load_games(self.crawler.get_list())

    def update_game_properties(self, game_info, old_folder_name):
        """Slaat gewijzigde metadata op en ververst de UI."""
        game_path = os.path.join(self.config.get_path(), old_folder_name)
        
        # Zorg dat de commando's correct worden gegenereerd op basis van de (nieuwe) paden en iso_path
        cfg_exec = os.path.join(game_path, "dosbox.cfg")
        self.crawler.create_dosbox_config(game_path, game_info.internal_exec, cfg_exec, iso_path=game_info.iso_path)
        game_info.exec_cmd = f'dosbox -conf "{cfg_exec}"'

        if game_info.internal_setup:
            cfg_setup = os.path.join(game_path, "dosbox_setup.cfg")
            self.crawler.create_dosbox_config(game_path, game_info.internal_setup, cfg_setup)
            game_info.setup_cmd = f'dosbox -conf "{cfg_setup}"'
        else:
            game_info.setup_cmd = None
        
        # Update Database
        self.db.save_game(old_folder_name, game_info)
        
        # Ververs de in-memory lijst van de crawler vanuit de DB
        self.crawler.build_list()

        # Reload UI
        self.view.load_games(self.crawler.get_list())

    def ignore_folder(self, folder_name):
        """Mark a folder as ignored by creating a marker file. Ignored folders stay in the library
        with their current metadata but will never be updated by a scanner again."""
        game_path = os.path.join(self.config.get_path(), folder_name)
        if os.path.exists(game_path):
            # Create the marker file so the Crawler skips this in the future
            marker_path = os.path.join(game_path, "GAMEDOT.EXC")
            with open(marker_path, 'w') as f:
                f.write("EXCLUDED FROM GAMEDOTEXE")
        
        self.crawler.build_list()
        self.view.load_games(self.crawler.get_list())

    def unignore_folder(self, folder_name):
        """Remove the ignore marker so the folder can be scanned again."""
        game_path = os.path.join(self.config.get_path(), folder_name)
        marker_path = os.path.join(game_path, "GAMEDOT.EXC")
        if os.path.exists(marker_path):
            os.remove(marker_path)
        
        self.crawler.build_list()
        self.view.load_games(self.crawler.get_list())