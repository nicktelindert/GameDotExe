class GameInfo:
    def __init__(self, folder_name, name, icon_path, exec_cmd=None, setup_cmd=None, compatibility=None, release_date=None, internal_exec=None, internal_setup=None, iso_path=None):
        self.folder_name = folder_name
        self.name = name
        self.icon_path = icon_path
        self.exec_cmd = exec_cmd
        self.setup_cmd = setup_cmd
        self.compatibility = compatibility
        self.release_date = release_date
        self.internal_exec = internal_exec
        self.internal_setup = internal_setup
        self.iso_path = iso_path