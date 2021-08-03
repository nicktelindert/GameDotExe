# README

GameDotExe just does one thing and that is launching ms-dos games.
The first time you start the program it will ask you where you ms-dos games are stored. Then it will scan you game folders for an .ini file the .ini file needs to have the same name as the game folder. 

## folder structure
- gamename/data/[your game data]
- gamename/gamename.ini
- gamename/gamename.icon

## ini file example
[Gameinfo]  
name = Titanic Adventure Out Of Time  
 icon = titanic.ico  
 exec = C:\gamedir\game.exe  

The launcher will then  create a dosbox.cfg file with the correct information which then will be used to launch the game.

## Requirements
- xdg
- ConfigParser
- Pixbuf
- gi
- os
- pathlib

