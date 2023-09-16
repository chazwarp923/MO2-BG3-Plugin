# -*- encoding: utf-8 -*-

# import clr
import mobase


def generateSettings(ml: mobase.IModList) -> bool:
    # clr.AddReference("LSLib")
    print(ml.allMods())
    return True
