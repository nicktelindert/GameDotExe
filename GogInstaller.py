import subprocess
import os
import shutil
import tempfile
from pathlib import Path
from DosGameDatabase import DosGameDatabase

class GogInstaller:
    def __init__(self, games_base_path):
        self.games_base_path = games_base_path

    def install(self, installer_path, game_name):
        dest_path = os.path.join(self.games_base_path, game_name)
        if os.path.exists(dest_path):
            raise Exception(f"De map '{game_name}' bestaat al in je games-map.")

        # Gebruik een tijdelijke map voor extractie
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # Voer innoextract uit
                # -d specificeert de doelmap
                subprocess.run(["innoextract", "-d", tmp_dir, installer_path], check=True, capture_output=True)
            except FileNotFoundError:
                raise Exception("innoextract is niet gevonden op dit systeem. Installeer innoextract om GOG installers te gebruiken.")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Extractie mislukt: {e.stderr.decode('utf-8')}")

            # --- Nieuwe logica voor het vinden van de game folder ---
            game_root_in_tmp = None
            
            # Prioriteit 1: Zoek naar executables die matchen met de game_name
            executables = []
            allowed_extensions = ['.exe', '.com', '.bat']
            blacklist_terms = ['setup', 'install', 'setsound', 'uninstall']
            first_letter = game_name[0].lower()

            for p in Path(tmp_dir).rglob('*'):
                if p.is_file() and p.suffix.lower() in allowed_extensions:
                    if not any(term in p.name.lower() for term in blacklist_terms):
                        # Verplichte eerste letter match
                        if p.name.lower().startswith(first_letter):
                            executables.append(p)
            
            # Probeer de meest relevante executable te vinden
            best_match_exe_path = None
            game_name_lower = game_name.lower()

            # Gebruik dezelfde scoring als in Crawler
            def score_gog_exe(p_obj):
                name_lower = p_obj.stem.lower()
                # Extensie prioriteit: .bat (0), .com (1), .exe (2)
                ext = p_obj.suffix.lower()
                ext_priority = 0 if ext == '.bat' else (1 if ext == '.com' else 2)
                
                # Check ook tegen bekende DB
                is_known = 0 if DosGameDatabase.get_executable(game_name) == p_obj.name else 1
                partial = 0 if (game_name_lower in name_lower or name_lower in game_name_lower) else 1
                return (is_known, partial, ext_priority, len(p_obj.parts), len(name_lower))

            executables.sort(key=score_gog_exe)

            for exe_path in executables:
                best_match_exe_path = exe_path
                break

            if best_match_exe_path:
                game_root_in_tmp = best_match_exe_path.parent
            else:
                # Fallback: If no specific executable match, try 'app' folder or the root tmp_dir
                src_app_folder = os.path.join(tmp_dir, "app")
                if os.path.exists(src_app_folder) and os.path.isdir(src_app_folder):
                    game_root_in_tmp = Path(src_app_folder)
                else:
                    game_root_in_tmp = Path(tmp_dir) # Assume game is directly in tmp_dir

            if not game_root_in_tmp or not game_root_in_tmp.exists():
                raise Exception(f"Kon de game-bestanden niet vinden in de geëxtraheerde GOG installer voor '{game_name}'.")

            # --- Kopieer de game-bestanden en ruim op ---
            os.makedirs(dest_path, exist_ok=True)

            # GOG-specifieke bestanden/mappen die we willen negeren
            gog_ignore_patterns = [
                "goggame-*.dll", "goggame-*.exe", "goggame-*.dat", # GOG DRM/launcher files
                "dosbox_*.conf", "dosbox_*.bat", # GOG's custom DOSBox configs/launchers
                "__redist", "__support", # Common GOG support folders
                "manual.pdf", "wallpaper.jpg", # Extras, usually not part of the game itself
                "eula.txt", "readme.txt" # Common documentation
            ]
            
            # Custom ignore function for shutil.copytree
            def ignore_gog_files(directory, contents):
                ignored = []
                for item in contents:
                    item_path = Path(directory) / item
                    item_lower = item.lower()

                    # Check against specific GOG patterns
                    if any(Path(item).match(pattern) for pattern in gog_ignore_patterns):
                        ignored.append(item)
                        continue
                    
                    # Ignore common non-game folders
                    if item_path.is_dir() and item_lower in ["__redist", "__support", "docs", "manuals", "sound", "music"]:
                        ignored.append(item)
                        continue
                    
                    # Ignore common non-game files
                    if item_path.is_file() and item_lower in ["eula.txt", "readme.txt", "manual.pdf", "wallpaper.jpg"]:
                        ignored.append(item)
                        continue
                return ignored

            # Copy the contents of the identified game_root_in_tmp to dest_path
            # using the custom ignore function
            shutil.copytree(game_root_in_tmp, dest_path, ignore=ignore_gog_files, dirs_exist_ok=True)
        
        return dest_path