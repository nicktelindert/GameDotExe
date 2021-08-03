import configparser
import os
from GameInfo import GameInfo

class Crawler:
    games_list = []
    def __init__(self, path):
        print("Found game path:" + path)
        print("Search directories in " + path)
        print(os.listdir(path))
        for game in os.listdir(path):
            game_path = path + '/' + game + '/';
            ini_file = game_path + game + '.ini'
            cfg_file = game_path + 'dosbox.cfg'
            config = configparser.ConfigParser()
            config.read(ini_file)
            exec_path = config['Gameinfo']['exec']
            print(exec_path);
            if not os.path.isfile(cfg_file):
                config = configparser.ConfigParser()
                with open(cfg_file, 'a') as f:
                    f.write("[autoexec]\n")
                    f.write('MOUNT C ' + game_path + "data/\n")
                    f.write('C:\n')
                    f.write(exec_path)
                    f.close()

            if (os.path.isfile(ini_file) and os.path.isfile(cfg_file)):
                config = configparser.ConfigParser()
                config.read(ini_file)
                game_name = config['Gameinfo']['name']
                print("Found game:" + game_name)
                icon_file = game_path + config['Gameinfo']['icon']
                exec_cmd = "dosbox -conf " + cfg_file;
                game_info = GameInfo(game_name, exec_cmd, icon_file)
                self.games_list.append(game_info)

    def get_list(self):
        return self.games_list
