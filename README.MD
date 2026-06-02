# GameDotExe - A Modern DOSBox Game Launcher

GameDotExe is a user-friendly DOSBox game launcher, designed to make managing and playing your favorite MS-DOS games as easy as possible. The application has been completely rewritten in Python with a modern Qt6 (PySide6) graphical interface.

## Features

-   **Clear Appearance**: A modern and clean design that makes finding and launching your games easy.
-   **Automatically Find Your Games**: Simply point to the folder where your games are located, and the app will find them itself.
-   **Smart Launch Help**: In most cases, the app knows which file to use to start the game, so you don't have to.
-   **Beautiful Pictures and Information**: Automatically fetches covers and the correct release dates from the internet, making your collection look great.
-   **No Difficult Settings**: The app handles the correct DOSBox settings behind the scenes. You no longer have to write complicated configuration files yourself.
-   **Directly Add Games from GOG.com**: Have you bought games on GOG? You can add them directly from the installation file. The app extracts only the necessary game files and leaves the redundant baggage behind.
-   **Easy Management**:
    -   **Playing**: Start your favorite classic with the touch of a button.
    -   **Set Up**: Easily perform sound settings or other setup options for a game via the menu.
    -   **Customize**: Want a different name, a different cover, or a different startup method? You can easily change everything yourself.
    -   **Clean Up**: Delete games you no longer play directly from the app, including all files on your disk.
-   **Lightning Fast**: Your library is stored intelligently, so the app is always ready for use, no matter how large your collection is.

## Installation

1.  **Python**: Ensure Python 3.8+ is installed.
2.  **Pip Dependencies**:
    ```bash
    pip install PySide6 requests
    ```
3.  **innoextract**: For importing GOG.com installers, `innoextract` is required. Install this via your operating system's package manager:
    -   **Debian/Ubuntu**: `sudo apt install innoextract`
    -   **Fedora**: `sudo dnf install innoextract`
    -   **Arch Linux**: `sudo pacman -S innoextract`
    -   **macOS (Homebrew)**: `brew install innoextract`
    -   **Windows**: Download the executable from the official innoextract website and add it to your PATH.

## Usage

1.  **First Startup**: On the first startup, the application will ask you to select the main folder where all your MS-DOS games are stored in subfolders.
2.  **Adding Games**:
    -   Place new game folders directly in the configured main folder.
    -   Use the "Install from GOG" button to import GOG.com installers.
3.  **Scanning**:
    -   The application automatically scans for new games on startup.
    -   Use the "Force Scan" button to rescan the entire library, or select a game and click "Force Scan" to refresh only that game.
4.  **Game Actions**:
    -   **Play**: Click the "Play" button under a game to start it.
    -   **Context Menu**: Right-click on a game in the list for extra options such as "Run Setup", "Edit Properties", and "Delete".
5.  **Search**: Use the search bar to quickly find games.

## Project Structure

-   `main.py`: Main application and GUI logic.
-   `Config.py`: Manages application configuration (games folder, log path).
-   `Crawler.py`: Scans game folders, detects executables, and integrates with metadata providers.
-   `DatabaseManager.py`: Handles all interaction with the SQLite database.
-   `GameInfo.py`: Data model for game information.
-   `MetadataProvider.py`: Abstract class for metadata providers, with `PCGamingWikiProvider` implementation.
-   `DosGameDatabase.py`: Loads known game-executable mappings from JSON.
-   `GogInstaller.py`: Logic for extracting and importing GOG.com installers.
-   `Dialog.py`: Simple dialog for folder selection.
-   `known_dos_games.json`: External database for known DOS games and their executables.
-   `assets/`: Contains standard icons and the `dosbox.cfg` template.
-   `~/.config/GameDotExe/`: Location for `config.ini`, `games.db`, `pcgamingwiki.log`, and the `artwork` cache.

## Translations (i18n)
GameDotExe supports English, Dutch, German, French, and Spanish. The language is automatically chosen based on your system settings.

To update translations:
1. Generate `.ts` files: `lupdate main.py MetadataProvider.py -ts translations/gamedotexe_nl.ts`  
2. Translate the text using **Qt Linguist**.
3. Compile to `.qm`: `lrelease translations/*.ts`  

## Generating AppImage

To build an AppImage yourself on Linux, you need the following extra tools in addition to the standard dependencies:

1.  **PyInstaller**: Used to bundle the Python application and its dependencies.
    ```bash
    pip install pyinstaller
    ```
2.  **appimagetool**: Download `appimagetool` from the go-appimage releases. Make the file executable (`chmod +x`) and ensure it is available in your PATH.

Once these tools are present, you can generate the AppImage package by running the script:
```bash
bash build_appimage.sh
```

### LATER
- Windows & Mac support
- Auto download DOSBOX when it is not installed?