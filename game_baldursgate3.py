# -*- encoding: utf-8 -*-

import os
from typing import List, Optional
from PyQt5.QtCore import QDir, QFileInfo

import mobase

from ..basic_features import BasicGameSaveGameInfo
from ..basic_game import BasicGame

from .baldursgate3 import ModSettingsHelper


class BaldursGate3Game(BasicGame, mobase.IPluginFileMapper):
    Name = "Baldur's Gate 3 Support Plugin"
    Author = "chazwarp923"
    Version = "1.1.0"

    GameName = "Baldur's Gate 3"
    GameShortName = "baldursgate3"
    GameNexusName = "baldursgate3"
    GameValidShortNames = ["baldursgate3"]
    GameNexusId = 3474
    GameSteamId = [1086940]
    GameGogId = [1456460669]
    GameBinary = "bin/bg3.exe"
    GameDataPath = "Data"
    GameSaveExtension = "lsv"
    GameDocumentsDirectory = (
        os.getenv("LOCALAPPDATA") + "/Larian Studios/Baldur's Gate 3"
    )
    GameSavesDirectory = (
        os.getenv("LOCALAPPDATA")
        + "/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/Story"
    )

    DOCS_MOD_SPECIAL_NAME = "PAK_FILES"

    def __init__(self):
        BasicGame.__init__(self)
        mobase.IPluginFileMapper.__init__(self)

    def init(self, organizer: mobase.IOrganizer):
        super().init(organizer)

        self._featureMap[mobase.SaveGameInfo] = BasicGameSaveGameInfo(
            lambda s: s.replace(".lsv", ".webp")
        )

        self._featureMap[mobase.ModDataChecker] = BaldursGate3ModDataChecker()

        # callback = ModSettingsHelper.generateSettings()
        self._organizer.onAboutToRun(self.aboutToRunCallback)

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

    def mappings(self) -> List[mobase.Mapping]:
        map = []
        modDirs = [self.DOCS_MOD_SPECIAL_NAME]
        self._listDirsRecursive(modDirs, prefix=self.DOCS_MOD_SPECIAL_NAME)
        for dir_ in modDirs:
            for file_ in self._organizer.findFiles(path=dir_, filter=lambda x: True):
                m = mobase.Mapping()
                m.createTarget = True
                m.isDirectory = False
                m.source = file_
                m.destination = os.path.join(
                    self.documentsDirectory().absoluteFilePath("Mods"),
                    file_.split(self.DOCS_MOD_SPECIAL_NAME)[1].strip("\\").strip("/"),
                )
                map.append(m)
        return map

    def _listDirsRecursive(self, dirs_list, prefix=""):
        dirs = self._organizer.listDirectories(prefix)
        for dir_ in dirs:
            dir_ = os.path.join(prefix, dir_)
            dirs_list.append(dir_)
            self._listDirsRecursive(dirs_list, dir_)

    # def primarySources(
    # self,
    # ):  # Not sure this function does anything, but I don't know enough about python to dare remove it
    # return self.GameValidShortNames

    def aboutToRunCallback(self, path: str) -> bool:
        # ModSettingsHelper.generateSettings(self._organizer.modList())
        return True


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
            BaldursGate3Game.DOCS_MOD_SPECIAL_NAME,
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
                tree.move(src_file, "/PAK_FILES/", policy=mobase.IFileTree.MERGE)

        return tree
