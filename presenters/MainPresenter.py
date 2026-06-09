import os
import shutil
import sys
import platform
import subprocess
import shlex
from PySide6.QtCore import QCoreApplication

# Import from new package structure
# (Imports blijven gelijk)

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

    def _get_dosbox_path(self):
        """Centrale methode om de DOSBox executable te vinden op basis van OS."""
        exe_ext = ".exe" if platform.system() == "Windows" else ""
        bundled_dosbox = os.path.join(getattr(sys, '_MEIPASS', ''), f'dosbox{exe_ext}')
        
        dosbox_path = bundled_dosbox if os.path.exists(bundled_dosbox) else shutil.which("dosbox")

        if not dosbox_path and platform.system() == 'Darwin':
            mac_paths = [
                "/Applications/DOSBox.app/Contents/MacOS/DOSBox",
                os.path.expanduser("~/Applications/DOSBox.app/Contents/MacOS/DOSBox"),
                "/opt/homebrew/bin/dosbox",
                "/usr/local/bin/dosbox"
            ]
            for p in mac_paths:
                if os.path.exists(p):
                    dosbox_path = p
                    break
        return dosbox_path

    def launch_game(self, cmd):
        """Start de game via DOSBox met platform-specifieke paden en configuratie."""
        if not cmd:
            self.view.show_error(QCoreApplication.translate("MainPresenter", "Launch Error"), 
                                 QCoreApplication.translate("MainPresenter", "No valid startup command found for this game."))
            return

        dosbox_path = self._get_dosbox_path()
        if not dosbox_path:
            self.view.show_error(QCoreApplication.translate("MainPresenter", "Error"), 
                                 QCoreApplication.translate("MainPresenter", "DOSBox not found. Please install 'dosbox' to launch games."))
            return

        # 2. Parse het commando en valideer configuratie
        try:
            args = shlex.split(cmd)
            if args[0] == "dosbox":
                args[0] = dosbox_path
            
            if "-conf" in args:
                conf_idx = args.index("-conf") + 1
                if conf_idx < len(args) and not os.path.exists(args[conf_idx]):
                    self.view.show_error(QCoreApplication.translate("MainPresenter", "Config Error"), 
                                         QCoreApplication.translate("MainPresenter", "Configuration file not found:\n{0}").format(args[conf_idx]))
                    return

            # 3. Start het proces
            subprocess.Popen(args)
        except Exception as e:
            self.view.show_error(QCoreApplication.translate("MainPresenter", "Launch Error"), 
                                 QCoreApplication.translate("MainPresenter", "Could not start DOSBox: {0}").format(str(e)))

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
        try:
            # Helper voor kopiëren met voortgang
            def copy_with_progress(files, total_size):
                copied_total = 0
                for src, dst in files:
                    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                        while True:
                            buf = fsrc.read(1024 * 1024) # 1MB chunks
                            if not buf:
                                break
                            fdst.write(buf)
                            copied_total += len(buf)
                            # Update voortgang (0.0 tot 1.0)
                            self.view.set_progress(copied_total / total_size)

            # 1. Map voorbereiding
            self.view.show_progress(QCoreApplication.translate("MainPresenter", "Preparing folders..."))
            self.view.set_progress(0)
            game_path = os.path.join(self.config.get_path(), game_name)
            if os.path.exists(game_path):
                raise Exception(QCoreApplication.translate("MainPresenter", "The folder '{0}' already exists.").format(game_name))
            os.makedirs(game_path, exist_ok=True)

            # 2. ISO/CUE naar centrale opslag kopiëren
            # We gebruiken de config map als basis (gebaseerd op locatie van de DB)
            safe_game_name = self.crawler._get_safe_filename(game_name)
            config_dir = os.path.dirname(self.db.db_path)
            iso_storage_root = os.path.join(config_dir, "ISOS", safe_game_name)
            os.makedirs(iso_storage_root, exist_ok=True)

            original_iso_name = os.path.basename(iso_path)
            new_iso_path = os.path.join(iso_storage_root, original_iso_name)

            files_to_copy = [(iso_path, new_iso_path)]

            # Speciale afhandeling voor CUE bestanden (kopieer ook de gerefereerde BIN bestanden)
            if original_iso_name.lower().endswith(".cue"):
                src_dir = os.path.dirname(iso_path)
                try:
                    with open(iso_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if "FILE" in line.upper():
                                # Parse filename tussen quotes: FILE "GAME.BIN" BINARY
                                parts = line.split('"')
                                if len(parts) >= 2:
                                    bin_filename = parts[1]
                                    bin_src = os.path.join(src_dir, bin_filename)
                                    if os.path.exists(bin_src):
                                        files_to_copy.append((bin_src, os.path.join(iso_storage_root, bin_filename)))
                except Exception as e:
                    print(f"Warning: Could not parse CUE file for extra bins: {e}")

            # 3. Voer de kopieeractie uit met voortgang
            total_size = sum(os.path.getsize(s) for s, d in files_to_copy)
            self.view.show_progress(QCoreApplication.translate("MainPresenter", "Copying image files..."))
            copy_with_progress(files_to_copy, total_size)

            # Gebruik vanaf nu het nieuwe pad voor de installatie en database
            active_iso_path = new_iso_path

            # Maak een tijdelijke DOSBox config om de installer te draaien
            self.view.show_progress(QCoreApplication.translate("MainPresenter", "Starting installer..."))
            self.view.set_progress(1.0)
            cfg_file = os.path.join(game_path, "install_dosbox.cfg")
            with open(cfg_file, 'w') as f:
                ext = os.path.splitext(active_iso_path)[1].lower()
                mount_type = "cdrom" if ext in ['.cue', '.bin'] else "iso"
                f.write("[sdl]\n[autoexec]\n")
                f.write(f"MOUNT C \"{game_path}\"\n")
                f.write(f"IMGMOUNT D \"{active_iso_path}\" -t {mount_type}\n")
                f.write("ECHO --------------------------------------------------\n")
                f.write(f"ECHO  {QCoreApplication.applicationName().upper()} ISO INSTALLER\n")
                f.write("ECHO --------------------------------------------------\n")
                f.write("ECHO  IMPORTANT: When the installer asks for a path,\n")
                f.write("ECHO  ALWAYS install the game directly to C:\\\n")
                f.write("ECHO --------------------------------------------------\n")
                f.write("PAUSE\n")
                f.write("D:\n")
                f.write("autorun.bat\n")
                # Probeer setup of install
                f.write("setup.exe\n")
                f.write("setup.bat\n")
                
                f.write("install.exe\n")
                f.write("install.bat\n")

                f.write("PAUSE\n")
                f.write("EXIT\n")

            # Gebruik de centrale helper voor DOSBox detectie
            dosbox_cmd = self._get_dosbox_path()
            
            if not dosbox_cmd:
                raise Exception(QCoreApplication.translate("MainPresenter", "DOSBox binary not found."))

            subprocess.run([dosbox_cmd, "-conf", cfg_file])

            # Ruim tijdelijke config op
            if os.path.exists(cfg_file):
                os.remove(cfg_file)

            # Scan de library om de nieuwe game te detecteren
            self.force_scan()
            # Na de scan, haal de game op uit de DB en update de iso_path.
            game_info = self.db.get_game(game_name)
            if game_info:
                # Stel het nieuwe centrale iso_path in op het GameInfo object
                game_info.iso_path = active_iso_path
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
        self.view.show_progress(QCoreApplication.translate("MainPresenter", "Deleting files..."))
        # 1. Verwijder uit database
        self.db.delete_game(game_info.folder_name)
        # 2. Verwijder map van schijf
        game_path = os.path.join(self.config.get_path(), game_info.folder_name)
        if os.path.exists(game_path):
            shutil.rmtree(game_path)
        # 3. Verwijder bijbehorende ISO map
        iso_dir = os.path.join(os.path.dirname(self.db.db_path), "ISOS", game_info.folder_name)
        if os.path.exists(iso_dir):
            shutil.rmtree(iso_dir)
        # 3. Ververs lijst
        self.crawler.build_list(
            selection_callback=self.view.prompt_metadata_selection,
            exe_selection_callback=self.view.prompt_exe_selection
        )
        self.view.load_games(self.crawler.get_list())

    def update_game_properties(self, game_info, old_folder_name):
        """Slaat gewijzigde metadata op en ververst de UI."""
        game_path = os.path.join(self.config.get_path(), old_folder_name)

        # Controleer of er een ISO in de centrale opslag staat
        iso_storage_dir = os.path.join(os.path.dirname(self.db.db_path), "ISOS", old_folder_name)
        detected_iso = None
        if os.path.exists(iso_storage_dir):
            for f in os.listdir(iso_storage_dir):
                if f.lower().endswith(('.iso', '.cue', '.bin')):
                    if not detected_iso or f.lower().endswith('.cue'):
                        detected_iso = os.path.join(iso_storage_dir, f)
        
        game_info.iso_path = detected_iso or game_info.iso_path
        
        # Zorg dat de commando's correct worden gegenereerd op basis van de (nieuwe) paden en iso_path
        cfg_exec = os.path.join(game_path, "dosbox.cfg")
        self.crawler.create_dosbox_config(game_path, game_info.internal_exec, cfg_exec, iso_path=detected_iso)
        game_info.exec_cmd = f'dosbox -conf "{cfg_exec}"'

        if game_info.internal_setup:
            cfg_setup = os.path.join(game_path, "dosbox_setup.cfg")
            self.crawler.create_dosbox_config(game_path, game_info.internal_setup, cfg_setup, iso_path=detected_iso)
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