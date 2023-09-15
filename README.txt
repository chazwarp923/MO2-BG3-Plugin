OVERVIEW

Adding this plugin to your Mod Organizer 2 instance will give you basic BG3 support, including full nexus download support and all other mod organizer features you know and love, excluding per profile save management which may come at a later date.

Due to the way that BG3 loads its .pak files from the Local AppData folder, Keyzma's Root Builder Plugin is REQUIRED for this plugin to be able to load any .pak files. Without it this will only work for mods that places files in the games Data folder.

In my personal testing, this should be capable of loading dll mods, such as achievement enabler and script extender.

INSTALLATION

Go to your Mod Organizer 2 installation folder and navigate to "plugins/basic_games/games" and put "game_baldursgate3.py" in there.
Open an administrator command prompt (shift right click the start menu) then cd to your BG3 install folder (eg. "cd C:\Program files (x86)\steam\steamapps\common\Baldurs Gate 3") then run ' mklink /d "%CD%\Mods" "%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods" '