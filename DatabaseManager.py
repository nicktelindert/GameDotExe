import sqlite3
from contextlib import contextmanager
from GameInfo import GameInfo

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_table()

    @contextmanager
    def _get_conn(self):
        """Context manager om row_factory en verbinding automatisch te beheren."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _create_table(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    folder_name TEXT PRIMARY KEY,
                    display_name TEXT,
                    icon_path TEXT,
                    exec_cmd TEXT,
                    setup_cmd TEXT,
                    compatibility TEXT,
                    release_date TEXT,
                    internal_exec TEXT,
                    internal_setup TEXT
                )
            """)

            # Migratie: Controleer of iso_path kolom bestaat, zo niet: voeg toe
            cursor = conn.execute("PRAGMA table_info(games)")
            columns = [row['name'] for row in cursor.fetchall()]
            if 'iso_path' not in columns:
                conn.execute("ALTER TABLE games ADD COLUMN iso_path TEXT")

    def get_game(self, folder_name):
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM games WHERE folder_name = ?", (folder_name,))
            row = cursor.fetchone()
            if row:
                return GameInfo(
                    folder_name=row['folder_name'],
                    name=row['display_name'],
                    icon_path=row['icon_path'],
                    exec_cmd=row['exec_cmd'],
                    setup_cmd=row['setup_cmd'],
                    compatibility=row['compatibility'],
                    release_date=row['release_date'],
                    internal_exec=row['internal_exec'],
                    internal_setup=row['internal_setup'],
                    iso_path=row['iso_path']
                )
        return None

    def save_game(self, folder_name, game_info):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO games (
                    folder_name, display_name, icon_path, exec_cmd, 
                    setup_cmd, compatibility, release_date, 
                    internal_exec, internal_setup, iso_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (folder_name, game_info.name, game_info.icon_path, 
                  game_info.exec_cmd, game_info.setup_cmd, 
                  game_info.compatibility, game_info.release_date,
                  game_info.internal_exec, game_info.internal_setup, game_info.iso_path))
            conn.commit()

    def get_all_games(self):
        games = []
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM games")
            for row in cursor.fetchall():
                games.append(GameInfo(
                    folder_name=row['folder_name'],
                    name=row['display_name'],
                    icon_path=row['icon_path'],
                    exec_cmd=row['exec_cmd'],
                    setup_cmd=row['setup_cmd'],
                    compatibility=row['compatibility'],
                    release_date=row['release_date'],
                    internal_exec=row['internal_exec'],
                    internal_setup=row['internal_setup'],
                    iso_path=row['iso_path']
                ))
        return games

    def clear_database(self):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM games")
            conn.commit()

    def delete_game(self, folder_name):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM games WHERE folder_name = ?", (folder_name,))
            conn.commit()