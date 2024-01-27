""" Init (all)Players all status point
"""
import os

from lib.sav_types.type import LevelSav
from lib.sav_types.utilType import Null

from lib.utils.level_util import loadSavJson, dumpSavJson
from lib.utils.charactersave_util import getRawPlayers

file_path = os.path.join(os.path.dirname(__file__), "Level.sav.json")
jsonData = loadSavJson(file_path)

saveData = LevelSav(**jsonData)

rawPlayers = getRawPlayers(saveData)
 
for rawPlayer in rawPlayers:
    totalStatusPoint = 0
    leftedValues = 0
    rawStatusPoints = rawPlayer.value.RawData.value.object.SaveParameter.value.GotStatusPointList.value.values
    for rawStatusPoint in rawStatusPoints:
        if rawStatusPoint.StatusName.value == "\u6355\u7372\u7387":
            continue
        totalStatusPoint += rawStatusPoint.StatusPoint.value
        rawStatusPoint.StatusPoint.value = 0
    if(rawPlayer.value.RawData.value.object.SaveParameter.value.UnusedStatusPoint):
        leftedValues = rawPlayer.value.RawData.value.object.SaveParameter.value.UnusedStatusPoint.value
    if leftedValues > 0 :
        rawPlayer.value.RawData.value.object.SaveParameter.value.UnusedStatusPoint.value += totalStatusPoint
    elif leftedValues < 0:
        rawPlayer.value.RawData.value.object.SaveParameter.value.UnusedStatusPoint.value = totalStatusPoint
    else:
        rawPlayer.value.RawData.value.object.SaveParameter.value.UnusedStatusPoint = {"id": Null(), "value": totalStatusPoint, "type": "IntProperty"}

output_path = "initedPlayersPoint.json"
dumpSavJson(output_path, saveData)
