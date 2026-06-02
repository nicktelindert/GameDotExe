import configparser
import os
from shutil import copyfile
from pathlib import Path
import requests
from GameInfo import GameInfo
from MetadataProvider import PCGamingWikiProvider
from DosGameDatabase import DosGameDatabase

class Crawler:
    def __init__(self, path, db_manager, metadata_provider=None, log_path=None, artwork_dir=None):
        self.base_path = path
        self.db = db_manager
        self.assets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        
        # Gebruik de meegegeven artwork_dir of val terug op de assets dir
        self.artwork_dir = artwork_dir or self.assets_dir
        if not os.path.exists(self.artwork_dir):
            os.makedirs(self.artwork_dir, exist_ok=True)
            
        self.metadata_provider = metadata_provider or PCGamingWikiProvider(log_path=log_path)
        self.games = []

    def build_list(self, force_scan=False, selection_callback=None, exe_selection_callback=None, target_folder=None):
        if not self.base_path or not os.path.exists(self.base_path):
            return

        # 1. Update/Toevoegen van metadata voor de relevante mappen
        for entry in os.scandir(self.base_path):
            if entry.is_dir():
                # Als we een target_folder hebben, negeer de rest
                if target_folder and entry.name != target_folder:
                    continue

                existing_game = self.db.get_game(entry.name)
                if existing_game and not force_scan:
                    continue

                game_info = self._process_game_folder(entry, selection_callback, exe_selection_callback)
                if game_info:
                    self.db.save_game(entry.name, game_info)

        # 2. Herbouw de in-memory lijst op basis van wat er op schijf staat
        self.games = []
        for entry in os.scandir(self.base_path):
            if entry.is_dir():
                game_info = self.db.get_game(entry.name)
                if game_info:
                    self.games.append(game_info)

    def _process_game_folder(self, entry, selection_callback, exe_selection_callback):
        game_path = entry.path
        game_name = entry.name
        ini_file = os.path.join(game_path, f"{game_name}.ini")
        cfg_file = os.path.join(game_path, 'dosbox.cfg')
        cfg_setup_file = os.path.join(game_path, 'dosbox_setup.cfg')
        
        # Gebruik de folder naam als basis voor de zoekopdracht
        display_name = game_name
        exec_path = self._find_executable(game_path, display_name)
        setup_exe = self._find_setup_executable(game_path)
        
        if os.path.isfile(ini_file):
            config = configparser.ConfigParser()
            config.read(ini_file)
            display_name = config.get('Gameinfo', 'name', fallback=game_name)
            if config.has_option('Gameinfo', 'exec'):
                exec_path = config.get('Gameinfo', 'exec')

        if not exec_path:
            if exe_selection_callback:
                exec_path = exe_selection_callback(game_path)
            
            if not exec_path:
                print(f"Geen executable gevonden in {game_name}, spel wordt overgeslagen.")
                return None

        # We mounten de game_path zelf als C:
        self.create_dosbox_config(game_path, exec_path, cfg_file)
        
        setup_cmd = None
        if setup_exe:
            self.create_dosbox_config(game_path, setup_exe, cfg_setup_file)
            setup_cmd = f'dosbox -conf "{cfg_setup_file}"'

        # Metadata selectie
        matches = self.metadata_provider.search_matches(display_name)
        selected_title = display_name
        
        if len(matches) > 1 and selection_callback:
            selected_title = selection_callback(display_name, matches)
        elif len(matches) == 1:
            selected_title = matches[0]

        meta = self.metadata_provider.fetch_metadata(selected_title)
        
        # Artwork afhandeling
        icon_path = os.path.join(self.assets_dir, "default_icon.svg")
        if meta["icon_url"]:
            icon_path = self._download_artwork(game_name, meta["icon_url"])

        exec_cmd = f'dosbox -conf "{cfg_file}"'
        return GameInfo(game_name, display_name, icon_path, exec_cmd, setup_cmd, meta["compatibility"], meta["release_date"], exec_path, setup_exe)

    def _find_executable(self, path, game_name):
        """Zoekt naar de meest logische executable in de map."""
        # Stap 1: Check de bekende database
        known_exe = DosGameDatabase.get_executable(game_name)
        if known_exe:
            potential_path = os.path.join(path, known_exe)
            if os.path.exists(potential_path):
                return known_exe

        allowed_extensions = ['.exe', '.com', '.bat']
        blacklist_terms = ['setup', 'install', 'setsound', 'uninstall'] # Removed duplicate 'install'
        first_letter = game_name[0].lower()
        
        found_files = []
        for p in Path(path).rglob('*'):
            if p.is_file() and p.suffix.lower() in allowed_extensions:
                # Controleer of de bestandsnaam (lowercase) geen blacklisted term bevat
                if not any(term in p.name.lower() for term in blacklist_terms):
                    # MOET beginnen met de eerste letter
                    if p.name.lower().startswith(first_letter):
                        found_files.append(p)
        
        if found_files:
            # Scoring systeem voor sorteren:
            # 1. Bevat de gamenaam (gedeeltelijke match) -> hoogste prio
            # 2. Kortste naam (vaak de hoofd-exe) -> tweede prio
            def score_exe(p_obj):
                name_lower = p_obj.stem.lower()
                game_lower = game_name.lower()
                
                # Extensie prioriteit: .bat (0), .com (1), .exe (2)
                ext = p_obj.suffix.lower()
                ext_priority = 0 if ext == '.bat' else (1 if ext == '.com' else 2)
                
                # Is het een gedeeltelijke match? (bijv 'jazz' in 'Jazz Jackrabbit')
                partial_match = 0 if (name_lower in game_lower or game_lower in name_lower) else 1
                
                # We willen partial_match=0 eerst, dan extensie prioriteit, dan kortste lengte
                return (partial_match, ext_priority, len(name_lower), name_lower)

            found_files.sort(key=score_exe)
            
            return os.path.relpath(found_files[0], path).replace('/', '\\')
        return None

    def _find_setup_executable(self, path):
        """Zoekt specifiek naar setup of sound configuratie bestanden."""
        setup_patterns = ['setup.exe', 'setsound.exe', 'install.exe', 'sndsetup.exe', 'sound.exe', 'setup.bat', 'install.bat']
        for p in Path(path).rglob('*'):
            if p.is_file() and p.name.lower() in setup_patterns:
                # Relatief pad t.o.v. de game folder voor DOSBox mount
                return os.path.relpath(p, path).replace('/', '\\')
        return None

    def _download_artwork(self, name, url):
        cache_path = os.path.join(self.artwork_dir, f"{name}.jpg")
        if not os.path.exists(cache_path):
            try:
                headers = {'User-Agent': 'GameDotExe/1.0 (MS-DOS Launcher; +https://github.com/nick/GameDotExe)'}
                r = requests.get(url, stream=True, timeout=5, headers=headers)
                
                # Controleer status code
                if r.status_code != 200:
                    print(f"Download error voor {name}: HTTP {r.status_code}")
                    return os.path.join(self.assets_dir, "default_icon.svg")
                
                # Controleer mimetype (Content-Type)
                content_type = r.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print(f"Download error voor {name}: Ongeldige mimetype {content_type} (waarschijnlijk HTML ontvangen)")
                    return os.path.join(self.assets_dir, "default_icon.svg")

                with open(cache_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            except Exception as e:
                print(f"Fout bij downloaden artwork voor {name}: {e}")
                return os.path.join(self.assets_dir, "default_icon.svg")
        return cache_path

    def get_list(self):
        return self.games

    def create_dosbox_config(self, mount_path, exec_path, cfg_file):
        template = os.path.join(self.assets_dir, 'dosbox.cfg')
        if os.path.exists(template):
            copyfile(template, cfg_file)
            with open(cfg_file, 'a') as f:
                f.write(f"\n\n[autoexec]\nMOUNT C \"{mount_path}\"\nC:\n{exec_path}\nexit\n")
