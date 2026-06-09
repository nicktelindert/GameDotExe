import sqlite3
import os
import inspect
from core.GameInfo import GameInfo

class DatabaseManager:
    DB_VERSION = 2  # Verhoog dit nummer bij elke schemawijziging

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._migrate_database()

    def __del__(self):
        """Zorgt ervoor dat de verbinding wordt gesloten wanneer het object wordt vernietigd."""
        self.close()

    def _connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row # Maakt het makkelijker om kolommen bij naam te benaderen

    def _initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                folder_name TEXT PRIMARY KEY,
                name TEXT,
                icon_path TEXT,
                exec_cmd TEXT,
                setup_cmd TEXT,
                compatibility TEXT,
                release_date TEXT,
                internal_exec TEXT,
                internal_setup TEXT,
                iso_path TEXT,
                safe_folder_name TEXT -- Nieuwe kolom
            )
        """)
        self.conn.commit()
        # Stel de initiële databaseversie in
        cursor.execute(f"PRAGMA user_version = {self.DB_VERSION}")
        self.conn.commit()

    def _migrate_database(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA user_version")
        current_version = cursor.fetchone()[0]
        print(f"database version:{current_version}")

        if current_version < 1:
            # Dit is een gloednieuwe database of een zeer oude versie zonder user_version
            self._initialize_db()
            # We herladen de versie om te zien of we net v2 hebben aangemaakt
            cursor.execute("PRAGMA user_version")
            current_version = cursor.fetchone()[0]

        # Legacy fix: Altijd controleren op de oude kolomnaam 'display_name'
        cursor.execute("PRAGMA table_info(games)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'display_name' in columns and 'name' not in columns:
            print("Database migration: Renaming 'display_name' to 'name' for GameInfo compatibility.")
            cursor.execute("ALTER TABLE games RENAME COLUMN display_name TO name")
            self.conn.commit()

        if current_version < 2:
            # Migratie van versie 1 naar versie 2: Voeg safe_folder_name toe
            print("Migrating database from v1 to v2: Adding 'safe_folder_name' column.")
            try:
                cursor.execute("ALTER TABLE games ADD COLUMN safe_folder_name TEXT")
                # Vul de nieuwe kolom voor bestaande records
                # Dit vereist dat GameInfo de safe_folder_name berekent
                from utils.path_utils import get_safe_filename
                existing_games = self.get_all_games()
                for game in existing_games:
                    game.safe_folder_name = get_safe_filename(game.folder_name)
                    self.save_game(game.folder_name, game) # Sla bijgewerkte game op
                
                cursor.execute("PRAGMA user_version = 2")
                self.conn.commit()
                print("Database migration to v2 complete.")
            except sqlite3.OperationalError as e:
                if "duplicate column name: safe_folder_name" in str(e):
                    print("Column 'safe_folder_name' already exists, skipping migration step.")
                    cursor.execute("PRAGMA user_version = 2")
                    self.conn.commit()
                else:
                    raise e

        # Voeg hier meer migratiestappen toe voor toekomstige versies
        # if current_version < 3:
        #    ...

    def save_game(self, folder_name, game_info: GameInfo):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO games (
                folder_name, name, icon_path, exec_cmd, setup_cmd, compatibility, 
                release_date, internal_exec, internal_setup, iso_path, safe_folder_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game_info.folder_name, game_info.name, game_info.icon_path, game_info.exec_cmd,
            game_info.setup_cmd, game_info.compatibility, game_info.release_date,
            game_info.internal_exec, game_info.internal_setup, game_info.iso_path,
            game_info.safe_folder_name
        ))
        self.conn.commit()

    def get_game(self, folder_name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM games WHERE folder_name = ?", (folder_name,))
        row = cursor.fetchone()
        if row:
            # Maak een dictionary van de row en filter alleen de keys die GameInfo verwacht.
            # Dit voorkomt crashes als er onverwachte kolommen in de database staan.
            row_dict = dict(row)
            
            # Voor het geval de RENAME COLUMN niet heeft gewerkt (bijv. oude SQLite versie)
            if 'display_name' in row_dict and 'name' not in row_dict:
                row_dict['name'] = row_dict.pop('display_name')

            # Filter kolommen die niet in de __init__ van GameInfo voorkomen om TypeErrors te voorkomen
            sig = inspect.signature(GameInfo.__init__)
            valid_params = [p.name for p in sig.parameters.values() if p.name != 'self']
            filtered_dict = {k: v for k, v in row_dict.items() if k in valid_params}
            
            return GameInfo(**filtered_dict)

        return None

    def get_all_games(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM games")
        # Gebruik dezelfde get_game logica voor de hele lijst
        return [self.get_game(row['folder_name']) for row in cursor.fetchall()]

    def delete_game(self, folder_name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM games WHERE folder_name = ?", (folder_name,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None