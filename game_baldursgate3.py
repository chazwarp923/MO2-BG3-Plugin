# -*- encoding: utf-8 -*-

import os, shutil
from typing import List, Optional
from PyQt6.QtCore import QDir, QFileInfo, QDirIterator, QFile, QFileInfo

import mobase

from ..basic_features import BasicGameSaveGameInfo
from ..basic_features import BasicLocalSavegames
from ..basic_game import BasicGame

from .baldursgate3 import ModSettingsHelper


class BaldursGate3Game(BasicGame, mobase.IPluginFileMapper):
    Name = "Baldur's Gate 3 Support Plugin"
    Author = "chazwarp923"
    Version = "2.0.0"

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
        os.getenv("LOCALAPPDATA")
        + "/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/"
    )
    GameSavesDirectory = (
        os.getenv("LOCALAPPDATA")
        + "/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/Savegames/Story"
    )
    GameIniFiles = ["modsettings.lsx", "config.lsf", "profile8.lsf", "UILayout.lsx"]

    PAK_MOD_PREFIX = "PAK_FILES"
    SCRIPT_EXTENDER_CONFIG_PREFIX = "BG3SE_CONFIG"

    def __init__(self):
        BasicGame.__init__(self)
        mobase.IPluginFileMapper.__init__(self)

    def init(self, organizer: mobase.IOrganizer):
        super().init(organizer)

        self._register_feature(BasicGameSaveGameInfo(
            lambda s: s.with_suffix(".webp")
        ))

        self._register_feature(BaldursGate3ModDataChecker())

        self._register_feature(BasicLocalSavegames(self.savesDirectory()))

        #self._organizer.onAboutToRun(self.onAboutToRun)
        self._organizer.onFinishedRun(self.onFinishedRun)

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
        modDirs = [self.PAK_MOD_PREFIX]
        self._listDirsRecursive(modDirs, prefix=self.PAK_MOD_PREFIX)
        for dir_ in modDirs:
            for file_ in self._organizer.findFiles(path=dir_, filter=lambda x: True):
                m = mobase.Mapping()
                m.createTarget = True
                m.isDirectory = False
                m.source = file_
                m.destination = os.path.join(
                    QDir(
                        os.getenv("LOCALAPPDATA") + "/Larian Studios/Baldur's Gate 3/"
                    ).absoluteFilePath("Mods"),
                    file_.split(self.PAK_MOD_PREFIX)[1].strip("\\").strip("/"),
                )
                map.append(m)

        configDirs = [self.SCRIPT_EXTENDER_CONFIG_PREFIX]
        self._listDirsRecursive(configDirs, prefix=self.SCRIPT_EXTENDER_CONFIG_PREFIX)
        for dir_ in configDirs:
            for file_ in self._organizer.findFiles(path=dir_, filter=lambda x: True):
                m = mobase.Mapping()
                m.createTarget = True
                m.isDirectory = False
                m.source = file_
                m.destination = os.path.join(
                    QDir(
                        os.getenv("LOCALAPPDATA") + "/Larian Studios/Baldur's Gate 3/"
                    ).absoluteFilePath("Script Extender"),
                    file_.split(self.SCRIPT_EXTENDER_CONFIG_PREFIX)[1]
                    .strip("\\")
                    .strip("/"),
                )
                map.append(m)
        return map

    def _listDirsRecursive(self, dirs_list, prefix=""):
        dirs = self._organizer.listDirectories(prefix)
        for dir_ in dirs:
            dir_ = os.path.join(prefix, dir_)
            dirs_list.append(dir_)
            self._listDirsRecursive(dirs_list, dir_)

    def onAboutToRun(self, path: str) -> bool:
        ModSettingsHelper.generateSettings(
            self._organizer.modList(), self._organizer.profile()
        )
        return True

    def onFinishedRun(self, path: str, integer: int) -> bool:
        seDir = QDir(
            os.getenv("LOCALAPPDATA") + "/Larian Studios/Baldur's Gate 3/"
        ).absoluteFilePath("Script Extender")

        # it = QDirIterator(seDir)
        # while it.hasNext():
        # f = QFile(it.next())
        # if QFileInfo(f).fileName() != "." and QFileInfo(f).fileName() != "..":
        # if not QDir(self._organizer.overwritePath() + QFileInfo(f).fileName()).exists():
        # shutil.move(f.fileName(), self._organizer.overwritePath())
        # find a way to not call if directory already exists
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
            "Mods",
            "PakInfo",
            "PlayerProfiles",
            "Public",
            "Root",
            "Shaders",
            "Video",
            BaldursGate3Game.PAK_MOD_PREFIX,
        ]

        VALID_FILE_EXTENSIONS = [
            ".pak",
            ".dll",
        ]

        for src_file in files:
            for extension in VALID_FILE_EXTENSIONS:
                if src_file.name().lower().endswith(extension.lower()):
                    print("we should be fucking working ya twat")
                    return mobase.ModDataChecker.FIXABLE

        for src_folder in folders:
            for dst_folder in VALID_FOLDERS:
                if src_folder.name().lower() == dst_folder.lower():
                    return mobase.ModDataChecker.VALID

        for src_folder in folders:
            if src_folder.name().lower().endswith("bin"):
                return mobase.ModDataChecker.FIXABLE

        for src_folder in folders:
            if "ModFixer" in str(src_folder):
                return mobase.ModDataChecker.FIXABLE
            if src_folder in VALID_FOLDERS:
                print()
            else:
                print("Invalid Folder: " + str(src_folder))

        return mobase.ModDataChecker.INVALID

    def fix(self, tree: mobase.IFileTree) -> Optional[mobase.IFileTree]:
        folders: List[mobase.IFileTree] = []
        files: List[mobase.FileTreeEntry] = []
        for entry in tree:
            print("entry in fix: " + str(entry))
            if isinstance(entry, mobase.IFileTree):
                folders.append(entry)
            else:
                files.append(entry)

        for src_folder in folders:
            if src_folder.name().lower().endswith("bin".lower()):
                tree.move(src_folder, "/Root/", policy=mobase.IFileTree.MERGE)

        for src_file in files:
            if src_file.name().lower().endswith(".dll".lower()):
                tree.move(src_file, "/Root/bin/", policy=mobase.IFileTree.MERGE)

        for src_file in files:
            if src_file.name().lower().endswith(".pak".lower()):
                print("moving file")
                tree.move(src_file, "/PAK_FILES/", policy=mobase.IFileTree.MERGE)

        return tree
