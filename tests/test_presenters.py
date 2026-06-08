import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from presenters.MainPresenter import MainPresenter

class TestMainPresenter(unittest.TestCase):
    def setUp(self):
        self.mock_view = MagicMock()
        self.mock_config = MagicMock()
        self.mock_db = MagicMock()
        self.mock_crawler = MagicMock()
        self.presenter = MainPresenter(self.mock_view, self.mock_config, self.mock_db, self.mock_crawler)

    def test_filter_games_calls_view(self):
        # Test of de presenter de view vertelt om te filteren met lowercase
        self.presenter.filter_games("Jazz")
        self.mock_view.apply_filter.assert_called_with("jazz")

    def test_initial_load_calls_crawler_and_view(self):
        # Arrange
        mock_games = [MagicMock(name="Game1")]
        self.mock_crawler.get_list.return_value = mock_games
        
        # Act
        self.presenter.initial_load()
        
        # Assert
        self.mock_crawler.build_list.assert_called_once()
        self.mock_view.load_games.assert_called_with(mock_games)

    @patch('shutil.rmtree')
    @patch('os.path.exists')
    def test_delete_game_confirmed(self, mock_exists, mock_rmtree):
        # Test of een game correct wordt verwijderd na bevestiging
        mock_exists.return_value = True
        self.mock_config.get_path.return_value = "/games"
        self.mock_db.db_path = "/config/games.db" # Mock db_path for ISO cleanup
        game_info = MagicMock(folder_name="test_game")
        self.presenter.delete_game(game_info)
        self.mock_db.delete_game.assert_called_with("test_game")
        mock_rmtree.assert_any_call(os.path.join("/games", "test_game"))
        mock_rmtree.assert_any_call(os.path.join("/config", "ISOS", "test_game"))
        self.mock_view.load_games.assert_called()

if __name__ == '__main__':
    unittest.main()