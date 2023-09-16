import mobase

from .game_baldursgate3 import BaldursGate3Game
from .game_baldursgate3 import BaldursGate3ModDataChecker


def createPlugins() -> mobase.IPlugin:
    return [BaldursGate3Game(), BaldursGate3ModDataChecker()]
