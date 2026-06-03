import unittest
from pyfakefs.fake_filesystem_unittest import TestCase
from unittest.mock import MagicMock, patch
from Crawler import Crawler
import os

class TestCrawler(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.mock_db = MagicMock()
        self.mock_meta = MagicMock()
        
        # Maak noodzakelijke mappen en bestanden aan in het virtuele bestandssysteem
        self.fs.create_dir("/fake/path")
        self.fs.create_dir("/fake/assets")
        self.fs.create_file("/fake/assets/dosbox.cfg", contents="[sdl]\n")
        
        self.crawler = Crawler("/fake/path", self.mock_db, metadata_provider=self.mock_meta)
        self.crawler.assets_dir = "/fake/assets"
        self.crawler.artwork_dir = "/fake/assets"

    def test_build_list_skips_existing(self):
        # Maak een game map aan in het virtuele systeem
        self.fs.create_dir("/fake/path/Game1")
        
        # Simuleer dat game al in de DB staat
        self.mock_db.get_game.return_value = MagicMock()
        
        self.crawler.build_list(force_scan=False)
        
        # save_game mag niet aangeroepen worden als de game al bekend is en force_scan uit staat
        self.mock_db.save_game.assert_not_called()

    def test_find_executable_logic(self):
        # Maak bestanden aan in de virtuele folder
        game_dir = "/fake/path/jazz"
        self.fs.create_file(os.path.join(game_dir, "SETUP.EXE"))
        self.fs.create_file(os.path.join(game_dir, "JAZZ.EXE"))
        
        with patch('DosGameDatabase.DosGameDatabase.get_executable', return_value=None):
            # "Jazz" begint met 'J', dus SETUP.EXE moet genegeerd worden (begint met 'S')
            result = self.crawler._find_executable(game_dir, "Jazz")
            self.assertEqual(result, "JAZZ.EXE")

    def test_create_dosbox_config(self):
        game_path = "/fake/path/testgame"
        cfg_out = os.path.join(game_path, "dosbox.cfg")
        self.fs.create_dir(game_path)
        
        self.crawler.create_dosbox_config(game_path, "START.EXE", cfg_out)
        
        # Controleer of het bestand echt is aangemaakt en de juiste inhoud heeft
        self.assertTrue(os.path.exists(cfg_out))
        with open(cfg_out, "r") as f:
            content = f.read()
            self.assertIn('MOUNT C "/fake/path/testgame"', content)
            self.assertIn("START.EXE", content)

if __name__ == '__main__':
    unittest.main()