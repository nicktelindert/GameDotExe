import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from core.DatabaseManager import DatabaseManager
from core.GameInfo import GameInfo

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_games.db"
        self.db_manager = DatabaseManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_get_game(self):
        game = GameInfo(
            folder_name="jazz2",
            name="Jazz Jackrabbit 2",
            icon_path="jazz.png",
            release_date="1998"
        )
        self.db_manager.save_game("jazz2", game)
        
        retrieved = self.db_manager.get_game("jazz2")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Jazz Jackrabbit 2")
        self.assertEqual(retrieved.release_date, "1998")
        self.assertEqual(retrieved.folder_name, "jazz2")

    def test_delete_game(self):
        game = GameInfo("test", "Test", "icon.png")
        self.db_manager.save_game("test", game)
        self.db_manager.delete_game("test")
        
        self.assertIsNone(self.db_manager.get_game("test"))

    def test_get_all_games(self):
        game1 = GameInfo("g1", "Game 1", "i1.png")
        game2 = GameInfo("g2", "Game 2", "i2.png")
        self.db_manager.save_game("g1", game1)
        self.db_manager.save_game("g2", game2)
        
        all_games = self.db_manager.get_all_games()
        self.assertEqual(len(all_games), 2)
        names = [g.name for g in all_games]
        self.assertIn("Game 1", names)
        self.assertIn("Game 2", names)

if __name__ == '__main__':
    unittest.main()