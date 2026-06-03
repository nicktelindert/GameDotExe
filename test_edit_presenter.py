import unittest
from unittest.mock import MagicMock, patch
from EditPresenter import EditPresenter
import os

class TestEditPresenter(unittest.TestCase):
    def setUp(self):
        self.mock_view = MagicMock()
        self.mock_game_info = MagicMock()
        self.mock_game_info.folder_name = "OldFolder"
        self.mock_config = MagicMock()
        self.mock_config.get_path.return_value = "/games"
        self.mock_db = MagicMock()
        self.mock_main_presenter = MagicMock()
        self.presenter = EditPresenter(
            self.mock_view, 
            self.mock_game_info, 
            self.mock_config, 
            self.mock_db, 
            self.mock_main_presenter
        )

    def test_save_changes_no_rename(self):
        new_data = {
            'name': 'OldFolder',
            'exec': 'NEW.EXE',
            'setup': 'SETUP.EXE',
            'release_date': '1990',
            'icon_path': '/path/to/icon'
        }
        
        result = self.presenter.save_changes(new_data)
        
        self.assertTrue(result)
        self.assertEqual(self.mock_game_info.name, 'OldFolder')
        self.mock_main_presenter.update_game_properties.assert_called_once()

    @patch('os.path.exists')
    @patch('os.rename')
    def test_save_changes_with_rename(self, mock_rename, mock_exists):
        mock_exists.return_value = False
        new_data = {
            'name': 'NewFolder',
            'exec': 'START.EXE',
            'setup': '',
            'release_date': '1991',
            'icon_path': ''
        }
        
        result = self.presenter.save_changes(new_data)
        
        self.assertTrue(result)
        mock_rename.assert_called_with(
            os.path.join("/games", "OldFolder"),
            os.path.join("/games", "NewFolder")
        )
        self.mock_db.delete_game.assert_called_with("OldFolder")
        self.mock_main_presenter.force_scan.assert_called_with(target_folder="NewFolder")

if __name__ == '__main__':
    unittest.main()