# -*- encoding: utf-8 -*-

import os, shutil
from typing import List, Optional
from PyQt6.QtCore import QDir, QFileInfo, QDirIterator, QFile, QFileInfo, qDebug

import mobase

from ..basic_features import BasicGameSaveGameInfo, BasicLocalSavegames, BasicModDataChecker
from ..basic_game import BasicGame

from .baldursgate3 import ModSettingsHelper

# This plugin is made thanks to chazwarp923's plugin, I only modified it and expanded on it

class BaldursGate3Game(BasicGame, mobase.IPluginFileMapper):
    Name = "Baldur's Gate 3 Unofficial Support Plugin"
    Author = "Dragozino"
    Version = "1.0.0"

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
    SCRIPT_EXTENDER_CONFIG_PREFIX = "SE_CONFIG"

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

        self._organizer.onAboutToRun(self.onAboutToRun)
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
                m.isDirectory = os.path.isdir(file_)
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

    def onModChanged(self, mod) -> bool:
        modsDict = []
        modsDict.append(next(iter(mod)))
        ModSettingsHelper.generateSettings(self._organizer.modList(), self._organizer.profile(), modsDict)
        return True

    def onAboutToRun(self, mod):
        ModSettingsHelper.generateSettings(self._organizer.modList(), self._organizer.profile(), [])
        return True

    def onFinishedRun(self, path: str, integer: int) -> bool:
        seDir = os.path.join(os.getenv("LOCALAPPDATA"), "Larian Studios", "Baldur's Gate 3", "Script Extender")
        mo2_se_config_dir = os.path.join(self._organizer.overwritePath(), "SE_CONFIG")

        configDirs = [seDir]
        
        self._listDirsRecursive(configDirs, prefix=seDir)

        for dir_ in configDirs:
            for file_ in os.listdir(dir_):
                full_src_path = os.path.join(dir_, file_)
                relative_path = os.path.relpath(full_src_path, seDir)
                dest_path = os.path.join(mo2_se_config_dir, relative_path)
               
                if os.path.isdir(full_src_path):
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    
                    for root, subdirs, files in os.walk(full_src_path):
                        for subdir in subdirs:
                            subdir_src = os.path.join(root, subdir)
                            subdir_relative = os.path.relpath(subdir_src, seDir)
                            subdir_dest = os.path.join(mo2_se_config_dir, subdir_relative)
                            
                            if not os.path.exists(subdir_dest):
                                os.makedirs(subdir_dest)

                        for file_ in files:
                            file_src = os.path.join(root, file_)
                            file_relative = os.path.relpath(file_src, seDir)
                            file_dest = os.path.join(mo2_se_config_dir, file_relative)
                            
                            file_dest_dir = os.path.dirname(file_dest)
                            if not os.path.exists(file_dest_dir):
                                os.makedirs(file_dest_dir)
                            
                            shutil.move(file_src, file_dest)

                elif os.path.isfile(full_src_path):
                    dest_dir = os.path.dirname(dest_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    shutil.move(full_src_path, dest_path)
        
        return True

class BaldursGate3ModDataChecker(mobase.ModDataChecker):
    def __init__(self):
        super().__init__()

    def dataLooksValid(self, tree: mobase.IFileTree) -> mobase.ModDataChecker.CheckReturn:
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
            BaldursGate3Game.SCRIPT_EXTENDER_CONFIG_PREFIX,
        ]

        VALID_FILE_EXTENSIONS = [
            ".pak",
            ".dll",
            ".json"
        ]

        for mainFolder in folders:
            for validFolder in VALID_FOLDERS:
                if mainFolder.name().lower() == validFolder.lower():
                    return mobase.ModDataChecker.VALID

        for mainFile in files:
            for extension in VALID_FILE_EXTENSIONS:
                if mainFile.name().lower().endswith(extension.lower()) and mainFile.name() != "info.json":
                    return mobase.ModDataChecker.FIXABLE
                
        for mainFolder in folders:
            if mainFolder.name().lower() == "bin":
                return mobase.ModDataChecker.FIXABLE
            else:
                for mainFile in mainFolder:
                    for extension in VALID_FILE_EXTENSIONS:
                            if mainFile.name().lower().endswith(extension.lower()) and mainFile.name() != "info.json":
                                return mobase.ModDataChecker.FIXABLE
                
        for src_folder in folders:
            for dst_folder in VALID_FOLDERS:
                if src_folder.name().lower() == dst_folder.lower():
                    return mobase.ModDataChecker.VALID

        return mobase.ModDataChecker.INVALID

    def fix(self, tree: mobase.IFileTree) -> Optional[mobase.IFileTree]:
        folders: List[mobase.IFileTree] = []
        files: List[mobase.FileTreeEntry] = []
        for entry in tree:
            if isinstance(entry, mobase.IFileTree):
                folders.append(entry)
            else:
                files.append(entry)

        REMOVE_FILES = [
            "readme"
        ]
        REMOVE_FILE_EXTENSIONS = [
            ".url",
            ".html",
            ".ink"
        ]

        # Remove unnecessary files
        for mainFile in files:
            for extension in REMOVE_FILE_EXTENSIONS:
                if mainFile.name().lower().endswith(extension.lower()):
                     tree.remove(mainFile)
            for filename in REMOVE_FILES:
                if mainFile.name().lower() == filename:
                     tree.remove(mainFile)

            
        for mainFolder in folders:
            for mainFile in mainFolder:
                for extension in REMOVE_FILE_EXTENSIONS:
                    if mainFile.name().lower().endswith(extension.lower()):
                        tree.remove(mainFolder)
                for filename in REMOVE_FILES:
                    if mainFile.name().lower() == filename:
                       tree.remove(mainFolder)


        for mainFile in files:
            if mainFile.name().lower().endswith(".pak".lower()):
                if mainFile == None: continue
                tree.move(mainFile, "/PAK_FILES/", policy=mobase.IFileTree.MERGE)
            if mainFile.name().lower().endswith(".json".lower()) and mainFile.name() != "info.json":
                tree.move(mainFile, "/SE_CONFIG/", policy=mobase.IFileTree.MERGE)
                    
        for mainFolder in folders:
            if mainFolder.name().lower() == "bin":
                tree.move(mainFolder, "/Root/", policy=mobase.IFileTree.MERGE)
            else:
                for mainFile in mainFolder:
                    if mainFile == None: continue
                    if mainFile.name().lower().endswith(".pak".lower()):
                        tree.move(mainFile, "/PAK_FILES/", policy=mobase.IFileTree.MERGE)
                    if mainFile.name().lower().endswith(".json".lower()) and mainFile.name() != "info.json":
                        tree.move(mainFile, "/SE_CONFIG/", policy=mobase.IFileTree.MERGE)

        return tree
