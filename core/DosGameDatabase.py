import json
import os

class DosGameDatabase:
    """
    Een eenvoudige database met bekende DOS games en hun bijbehorende executables.
    Dit voorkomt gokwerk bij populaire titels.
    """
    _KNOWN_GAMES = {}
    _DB_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "known_dos_games.json")

    @classmethod
    def _load_games(cls):
        if not cls._KNOWN_GAMES: # Laad alleen als het nog niet geladen is
            try:
                with open(cls._DB_FILE, 'r') as f:
                    cls._KNOWN_GAMES = json.load(f)
            except FileNotFoundError:
                print(f"Waarschuwing: '{cls._DB_FILE}' niet gevonden. Bekende games database is leeg.")
                cls._KNOWN_GAMES = {}
            except json.JSONDecodeError:
                print(f"Fout: '{cls._DB_FILE}' bevat ongeldige JSON. Bekende games database is leeg.")
                cls._KNOWN_GAMES = {}

    @classmethod
    def get_executable(cls, game_name):
        cls._load_games() # Zorg ervoor dat de games geladen zijn
        return cls._KNOWN_GAMES.get(game_name.lower())