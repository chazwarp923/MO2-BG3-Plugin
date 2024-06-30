# -*- encoding: utf-8 -*-

import mobase
import os
import os.path
import json
from xml.dom import minidom
import uuid
from pathlib import Path
import enum


def generateSettings(modList: mobase.IModList, profile: mobase.IProfile) -> bool:
    KNOWN_BAD_MODS = [
            "PartyLimitBegone.pak",
            "LongRestBugfix.pak",
            "KvCampEvents.pak",
        ]
    modInfoDict = {}
    modSequence = modList.allModsByProfilePriority()
    #import all info.json files into a dictionary
    for mod in modSequence:
        info = modList.getMod(mod).absolutePath() + "\info.json"
        if os.path.isfile(info):
            file = open(info, 'r')
            fileBuff = file.read()
            modInfoDict[mod] = json.loads(fileBuff.replace('\'', ''))
            #modInfoDict[mod] = json.loads(file.read())
            file.close()
            
    #export all mods info into modsettings.lsx
    root = minidom.Document()
    save = root.createElement('save')
    root.appendChild(save)
    version = root.createElement('version')
    version.setAttribute('major', '4')
    version.setAttribute('minor', '0')
    version.setAttribute('revision', '9')
    version.setAttribute('build', '331')
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
    
    for mod in modSequence:
        if (int(modList.state(mod) / 2) % 2 != 0):#the enum value for active is 2 so if the state / 2 cast to an int % 2 isnt 0 then it's active
            shouldBeProcessed = False
            pakFileFolder = modList.getMod(mod).absolutePath() + "\PAK_FILES"
            info = modList.getMod(mod).absolutePath() + "\info.json"
            if os.path.isfile(info):
                shouldBeProcessed = True
            if os.path.isdir(pakFileFolder):
                files = os.listdir(pakFileFolder)
                files = [f for f in files if os.path.isfile(pakFileFolder+'/'+f)]
                files = [f for f in files if f.endswith(".pak")]
                #print(files)
                for file in files:
                    for pakFile in KNOWN_BAD_MODS:
                        if pakFile == file:
                            shouldBeProcessed = True
                            if(pakFile == "PartyLimitBegone.pak"):
                                #print('we made it here')
                                modInfoDict[mod] = json.loads('{"Mods":[{"Name":"PartyLimitBegone","Folder":"PartyLimitBegone","Version":"72198331526283264","UUID":"1d6c4030-67b9-4b0a-b3ab-caf6dd73d1af"}],"MD5":""}')
                                #print(modInfoDict[mod])
                            elif(pakFile == "LongRestBugfix.pak"):
                                modInfoDict[mod] = json.loads('{"Mods":[{"Name":"LongRestBugfix","Folder":"LongRestBugfix","Version":"36028797018963968","UUID":"aa64de03-6743-4a2f-97f7-55d9620bd01b"}],"MD5":""}')
                            elif(pakFile == "KvCampEvents.pak"):
                                modInfoDict[mod] = json.loads('{"Mods":[{"Name":"KvCampEvents","Folder":"KvCampEvents","Version":"562960690839552","UUID":"1b8d381f-6210-4473-85be-600457267a87"}],"MD5":""}')
            if shouldBeProcessed == True:
                #modUUID = uuid.uuid4()
                tlkMods = modInfoDict[mod]
                print(tlkMods)
                infojsonStr = str(tlkMods['Mods'])
                infojsonStr = infojsonStr.replace('\'', '"')
                infojsonStr = infojsonStr.replace('None', '"36028797018963968"')
                infojsonStr = infojsonStr[1:-1]
                infojsonDict = json.loads(infojsonStr)
                nodeModule = root.createElement('node')
                nodeModule.setAttribute('id', 'Module')
                nodeModOrderChildren.appendChild(nodeModule)
                attributeModOrderUUID = root.createElement('attribute')
                attributeModOrderUUID.setAttribute('id', 'UUID')
                attributeModOrderUUID.setAttribute('value', infojsonDict['UUID'])
                attributeModOrderUUID.setAttribute('type', 'FixedString')
                nodeModule.appendChild(attributeModOrderUUID)
                nodeModOrderChildren.appendChild(nodeModule)
                
                nodeModuleShortDesc = root.createElement('node')
                nodeModuleShortDesc.setAttribute('id', 'ModuleShortDesc')
                nodeModsChildren.appendChild(nodeModuleShortDesc)
                attributeFolder = root.createElement('attribute')
                attributeFolder.setAttribute('id', 'Folder')
                attributeFolder.setAttribute('value', infojsonDict['Folder'])
                attributeFolder.setAttribute('type', 'LSString')
                nodeModuleShortDesc.appendChild(attributeFolder)
                attributeMD5 = root.createElement('attribute')
                attributeMD5.setAttribute('id', 'MD5')
                attributeMD5.setAttribute('value', '')
                attributeMD5.setAttribute('type', 'LSString')
                nodeModuleShortDesc.appendChild(attributeMD5)
                attributeName = root.createElement('attribute')
                attributeName.setAttribute('id', 'Name')
                attributeName.setAttribute('value', infojsonDict['Name'])
                attributeName.setAttribute('type', 'LSString')
                nodeModuleShortDesc.appendChild(attributeName)
                attributeModsUUID = root.createElement('attribute')
                attributeModsUUID.setAttribute('id', 'UUID')
                attributeModsUUID.setAttribute('value', infojsonDict['UUID'])
                attributeModsUUID.setAttribute('type', 'FixedString')
                nodeModuleShortDesc.appendChild(attributeModsUUID)
                attributeVersion = root.createElement('attribute')
                attributeVersion.setAttribute('id', 'Version64')
                attributeVersion.setAttribute('value', infojsonDict['Version'])
                attributeVersion.setAttribute('type', 'int64')
                nodeModuleShortDesc.appendChild(attributeVersion)
                nodeModsChildren.appendChild(nodeModuleShortDesc)
                
                xml_str = root.toprettyxml(indent ="  ")
                outputPath = profile.absolutePath() + "\modsettings.lsx"
                with open(outputPath, "w") as f:
                    f.write(xml_str)
                    f.close()
    
    return True
    