# -*- encoding: utf-8 -*-

import os
from typing import List, Optional
from PyQt5.QtCore import QDir, QFileInfo
from pathlib import Path

import mobase

from ..basic_features import BasicGameSaveGameInfo
from ..basic_game import BasicGame


class BaldursGate3Game(BasicGame, mobase.IPluginFileMapper):
    Name = "Baldur's Gate 3 Support Plugin"
    Author = "chazwarp923"
    Version = "1.0.0"

    GameName = "Baldur's Gate 3"
    GameShortName = "baldursgate3"
    GameNexusName = "baldursgate3"
    GameValidShortNames = ["baldursgate3"]
    GameNexusId = 3474
    GameSteamId = [1086940]
    GameGogId = [1456460669]
    GameBinary = "bin/bg3.exe"
    # GameLauncher = "Launcher/LariLauncher.exe"
    GameDataPath = "Data"
    GameSaveExtension = "lsv"  # Not confirmed
    GameDocumentsDirectory = "%LOCALAPPDATA%/Larian Studios/" "Baldur's Gate 3"
    GameSavesDirectory = "%LOCALAPPDATA%/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/Story"

    def __init__(self):
        BasicGame.__init__(self)
        mobase.IPluginFileMapper.__init__(self)

    def init(self, organizer: mobase.IOrganizer):
        super().init(organizer)
        self._featureMap[mobase.SaveGameInfo] = BasicGameSaveGameInfo(
            lambda s: s.replace(".lsv", ".webp")
        )
        self._featureMap[mobase.ModDataChecker] = BaldursGate3ModDataChecker()

        # Create the symlink to the mods directory if it doesn't exist
        modsPath = Path(self.dataDirectory().absolutePath()).parent
        modsPath = modsPath / "Mods"
        if not os.path.exists(modsPath):
            dest = Path(os.getenv("LOCALAPPDATA"))
            dest = dest / "Larian Studios/Baldur's Gate 3/Mods"
            modsPath.symlink_to(dest)

        return True

    def executables(self):
        return [
            mobase.ExecutableInfo(
                "BG3 - Vulkan", QFileInfo(self.gameDirectory(), "bin/bg3.exe")
            ).withArgument("--skip-launcher"),
            mobase.ExecutableInfo(
                "BG3 - DX11", QFileInfo(self.gameDirectory(), "bin/bg3_dx11.exe")
            ).withArgument("--skip-launcher"),
            mobase.ExecutableInfo(
                "Larian Launcher",
                QFileInfo(self.gameDirectory(), "Launcher/LariLauncher.exe"),
            ),
        ]


class BaldursGate3ModDataChecker(mobase.ModDataChecker):
    def __init__(self):
        super().__init__()

    def dataLooksValid(
        self, tree: mobase.IFileTree
    ) -> mobase.ModDataChecker.CheckReturn:
        folders: List[mobase.IFileTree] = []
        files: List[mobase.FileTreeEntry] = []

        for entry in tree:
            if isinstance(entry, mobase.IFileTree):
                folders.append(entry)
            else:
                files.append(entry)

        VALID_FOLDERS = [
            "Cursors",
            "DLC",
            "Engine",
            "Fonts",
            "Generated",
            "Localization",
            "PakInfo",
            "PlayerProfiles",
            "Public",
            "Root",
            "Shaders",
            "Video",
        ]
        for src_folder in folders:
            for dst_folder in VALID_FOLDERS:
                if src_folder.name().lower() == dst_folder.lower():
                    return mobase.ModDataChecker.VALID

        VALID_FILE_EXTENSIONS = [
            ".pak",
        ]
        for src_file in files:
            for extension in VALID_FILE_EXTENSIONS:
                if src_file.name().lower().endswith(extension.lower()):
                    return mobase.ModDataChecker.FIXABLE

        for src_folder in folders:
            if src_folder.name().lower().endswith("bin"):
                return mobase.ModDataChecker.FIXABLE

        return mobase.ModDataChecker.INVALID

    def fix(self, tree: mobase.IFileTree) -> Optional[mobase.IFileTree]:
        folders: List[mobase.IFileTree] = []
        files: List[mobase.FileTreeEntry] = []
        for entry in tree:
            if isinstance(entry, mobase.IFileTree):
                folders.append(entry)
            else:
                files.append(entry)

        for src_folder in folders:
            if src_folder.name().lower().endswith("bin"):
                tree.move(src_folder, "/Root/", policy=mobase.IFileTree.MERGE)

        for src_file in files:
            if src_file.name().lower().endswith(".pak"):
                tree.move(src_file, "/Root/Mods/", policy=mobase.IFileTree.MERGE)

        return tree
