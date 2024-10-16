# -*- encoding: utf-8 -*-

import mobase
import os
import json
import subprocess
from pathlib import Path
import shutil
from xml.dom import minidom
import xml.etree.ElementTree as ET
from PyQt6.QtCore import QDir, QFileInfo, QDirIterator, QFile, QFileInfo, qDebug

script_dir = os.path.abspath(__file__)

root_folder = Path(__file__).parents[4]

divine_path = os.path.join(Path(script_dir).parent, 'tools', 'Divine.exe')

def __tr(self, string):
     return QCoreApplication.translate("NameOfPluginClass", string)
def display(self):  
     qDebug(self.__tr(string))

def find_meta_lsx(name, path): # Find meta.lsx in directory
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def extract_meta_lsx(pak_path, output_dir): # Extract meta.lsx from .pak file

    command = [
        str(divine_path),
        "-a", "extract-package",
        "-g", "bg3",
        "-s", str(pak_path),
        "-d", str(output_dir),
        "-x", "*/meta.lsx",
        "-l", "off"
    ]

    result = subprocess.run(
        command,
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(result)

    modinfo = {
                "Name": "Override_Mod",
                "UUID": "Override_Mod",
                "Folder": "Override_Mod",
                "Version": "Override_Mod",
                "MD5": "Override_Mod"
            }

    if result.returncode == 0:
        meta_lsx_path = find_meta_lsx('meta.lsx', output_dir)

        if meta_lsx_path:
            modinfo = parse_meta_lsx(meta_lsx_path)
          
    return modinfo

   

def get_attribute_value(node, attr_id): # Extract attribute value
    attribute = node.find(f".//attribute[@id='{attr_id}']")
    return attribute.get('value') if attribute is not None else None

def get_attribute(info, *keys): # Match json attributes
    for key in keys:
        if key in info:
            return info[key]
    return None

def parse_meta_lsx(meta_lsx_path): # Extract information from meta.lsx
    if meta_lsx_path:
        tree = ET.parse(str(meta_lsx_path))
        root = tree.getroot()
        module_info = root.find(".//node[@id='ModuleInfo']")
        mod_info = {
            'Folder': get_attribute_value(module_info, 'Folder'),
            'Name': get_attribute_value(module_info, 'Name'),
            'PublishHandle': get_attribute_value(module_info, 'PublishHandle'),
            'UUID': get_attribute_value(module_info, 'UUID'),
            'MD5': get_attribute_value(module_info, 'MD5'),
            'Version': get_attribute_value(module_info, 'Version64'),
        }
        return mod_info

def generateSettings(modList: mobase.IModList, profile: mobase.IProfile, modsDict: list = None) -> bool:
    #raise IndexError(divine_path)

    modInfoDict = {}
    modJsons = {}
    modSequence = modsDict if modsDict else modList.allModsByProfilePriority()

    temp_dir = os.path.join(Path(__file__).resolve().parent, 'temp_extracted') 

    # Extract meta.lsx from PAK Files
    for mod in modSequence:
        if (int(modList.state(mod) / 2) % 2 != 0):
            pakFileFolder = modList.getMod(mod).absolutePath() + "\\PAK_FILES"

            info = modList.getMod(mod).absolutePath() + "\\info.json"

            if os.path.exists(info):
                modJsons[mod] = info
                continue

            if os.path.isdir(pakFileFolder):
                modInfoDict[mod] = []
                files = os.listdir(pakFileFolder)
                files = [f for f in files if f.lower().endswith(".pak")]
                for file in files:
                    mod_temp_dir = os.path.join(temp_dir, mod, file.split(".")[0])
                    if not os.path.exists(mod_temp_dir):
                        os.makedirs(mod_temp_dir)

                    mod_info = extract_meta_lsx(os.path.join(pakFileFolder, file), mod_temp_dir)
                    if mod_info:
                        modInfoDict[mod].append(mod_info)

    # Add Gustav to modsettings.lsx
    root = minidom.Document()
    save = root.createElement('save')
    root.appendChild(save)
    version = root.createElement('version')
    version.setAttribute('major', '4')
    version.setAttribute('minor', '7')
    version.setAttribute('revision', '1')
    version.setAttribute('build', '3')
    save.appendChild(version)
    region = root.createElement('region')
    region.setAttribute('id', 'ModuleSettings')
    save.appendChild(region)
    nodeRoot = root.createElement('node')
    nodeRoot.setAttribute('id', 'root')
    region.appendChild(nodeRoot)
    nodeRootChildren = root.createElement('children')#the base element ModOrder and Mods nodes get appended to
    nodeRoot.appendChild(nodeRootChildren)

    nodeModOrder = root.createElement('node')
    nodeModOrder.setAttribute('id', 'ModOrder')
    nodeRootChildren.appendChild(nodeModOrder)
    nodeModOrderChildren = root.createElement('children')#the base element all "ModOrder" "Module" tags get appended to
    nodeModOrder.appendChild(nodeModOrderChildren)
    nodeModuleGustav = root.createElement('node')
    nodeModuleGustav.setAttribute('id', 'Module')
    nodeModOrderChildren.appendChild(nodeModuleGustav)
    attributeModOrderUUIDGustav = root.createElement('attribute')
    attributeModOrderUUIDGustav.setAttribute('id', 'UUID')
    attributeModOrderUUIDGustav.setAttribute('value', '28ac9ce2-2aba-8cda-b3b5-6e922f71b6b8')
    attributeModOrderUUIDGustav.setAttribute('type', 'FixedString')
    nodeModuleGustav.appendChild(attributeModOrderUUIDGustav)

    nodeMods = root.createElement('node')
    nodeMods.setAttribute('id', 'Mods')
    nodeRootChildren.appendChild(nodeMods)
    nodeModsChildren = root.createElement('children')#the base element all "Mods" "ModuleShortDesc" tags get appended to
    nodeMods.appendChild(nodeModsChildren)
    nodeModuleShortDescGustav = root.createElement('node')
    nodeModuleShortDescGustav.setAttribute('id', 'ModuleShortDesc')
    nodeModsChildren.appendChild(nodeModuleShortDescGustav)
    attributeFolderGustav = root.createElement('attribute')
    attributeFolderGustav.setAttribute('id', 'Folder')
    attributeFolderGustav.setAttribute('value', 'GustavDev')
    attributeFolderGustav.setAttribute('type', 'LSString')
    nodeModuleShortDescGustav.appendChild(attributeFolderGustav)
    attributeMD5Gustav = root.createElement('attribute')
    attributeMD5Gustav.setAttribute('id', 'MD5')
    attributeMD5Gustav.setAttribute('value', '5e66b6872b07a6b2283a4e4a9cccb325')
    attributeMD5Gustav.setAttribute('type', 'LSString')
    nodeModuleShortDescGustav.appendChild(attributeMD5Gustav)
    attributeNameGustav = root.createElement('attribute')
    attributeNameGustav.setAttribute('id', 'Name')
    attributeNameGustav.setAttribute('value', 'GustavDev')
    attributeNameGustav.setAttribute('type', 'LSString')
    nodeModuleShortDescGustav.appendChild(attributeNameGustav)
    attributeModsUUIDGustav = root.createElement('attribute')
    attributeModsUUIDGustav.setAttribute('id', 'UUID') 
    attributeModsUUIDGustav.setAttribute('value', '28ac9ce2-2aba-8cda-b3b5-6e922f71b6b8')
    attributeModsUUIDGustav.setAttribute('type', 'FixedString')
    nodeModuleShortDescGustav.appendChild(attributeModsUUIDGustav)
    attributeVersion64Gustav = root.createElement('attribute')
    attributeVersion64Gustav.setAttribute('id', 'Version64') 
    attributeVersion64Gustav.setAttribute('value', '144961545746289842')
    attributeVersion64Gustav.setAttribute('type', 'int64')
    nodeModuleShortDescGustav.appendChild(attributeVersion64Gustav)

    # Add info.json to mods that don't have it
    for mod in modSequence:
        if (int(modList.state(mod) / 2) % 2 != 0):
            info = modList.getMod(mod).absolutePath() + "\\info.json"

            if os.path.exists(info):
                continue

            if modInfoDict.get(mod):
                JSONdata = { "Mods": [] }
                for infojsonDict in modInfoDict[mod]:
                    JSONdata['Mods'].append(infojsonDict)

                    file_name = os.path.join(modList.getMod(mod).absolutePath(), 'info.json')

                    with open(file_name, 'w') as file:
                        json.dump(JSONdata, file, indent=4)
                        modJsons[mod] = modList.getMod(mod).absolutePath() + "\\info.json"

    # Generate modsettings.lsx
    for mod in modSequence:
        if (int(modList.state(mod) / 2) % 2 != 0):
            if modJsons.get(mod):
                with open(modJsons[mod], 'r') as file:
                    # modJsons
                    infoJson = json.load(file)

                    mods = infoJson.get('Mods') or infoJson.get('mods')

                    for mod in mods:
                        name = get_attribute(mod, 'Name', 'modName')
                        folder = get_attribute(mod, 'Folder', 'folderName')
                        uuid = get_attribute(mod, 'UUID', 'uuid')
                        version = get_attribute(mod, 'Version', 'version')

                        if name == "Override_Mod":
                            continue

                        nodeModule = root.createElement('node')
                        nodeModule.setAttribute('id', 'Module')
                        nodeModOrderChildren.appendChild(nodeModule)
                        attributeModOrderUUID = root.createElement('attribute')
                        attributeModOrderUUID.setAttribute('id', 'UUID')
                        attributeModOrderUUID.setAttribute('value', uuid)
                        attributeModOrderUUID.setAttribute('type', 'FixedString')
                        nodeModule.appendChild(attributeModOrderUUID)
                        nodeModOrderChildren.appendChild(nodeModule)

                        nodeModuleShortDesc = root.createElement('node')
                        nodeModuleShortDesc.setAttribute('id', 'ModuleShortDesc')
                        nodeModsChildren.appendChild(nodeModuleShortDesc)
                        attributeFolder = root.createElement('attribute')
                        attributeFolder.setAttribute('id', 'Folder')
                        attributeFolder.setAttribute('value', folder)
                        attributeFolder.setAttribute('type', 'LSString')
                        nodeModuleShortDesc.appendChild(attributeFolder)
                        attributeMD5 = root.createElement('attribute')
                        attributeMD5.setAttribute('id', 'MD5')
                        attributeMD5.setAttribute('value', '')
                        attributeMD5.setAttribute('type', 'LSString')
                        nodeModuleShortDesc.appendChild(attributeMD5)
                        attributeName = root.createElement('attribute')
                        attributeName.setAttribute('id', 'Name')
                        attributeName.setAttribute('value', name)
                        attributeName.setAttribute('type', 'LSString')
                        nodeModuleShortDesc.appendChild(attributeName)
                        attributeModsUUID = root.createElement('attribute')
                        attributeModsUUID.setAttribute('id', 'UUID')
                        attributeModsUUID.setAttribute('value', uuid)
                        attributeModsUUID.setAttribute('type', 'FixedString')
                        nodeModuleShortDesc.appendChild(attributeModsUUID)
                        attributeVersion = root.createElement('attribute')
                        attributeVersion.setAttribute('id', 'Version64')
                        attributeVersion.setAttribute('value', version)
                        attributeVersion.setAttribute('type', 'int64')
                        nodeModuleShortDesc.appendChild(attributeVersion)
                        nodeModsChildren.appendChild(nodeModuleShortDesc)

    xml_str = root.toprettyxml(indent="  ")
    outputPath = profile.absolutePath() + "\\modsettings.lsx"
    with open(outputPath, "w") as f:
        f.write(xml_str)
        f.close()

    temp_dir = Path(temp_dir)

    if os.path.exists(temp_dir):
        for item in temp_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"Error deleting {item}: {e}")
                

    return True
